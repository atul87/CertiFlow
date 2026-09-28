"""
Organization membership, invitations, suspension, and ownership transfer service (P8).
"""
from __future__ import annotations
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError, ConflictError, ForbiddenError
from app.core.security import get_password_hash, create_access_token, create_refresh_token
from app.repositories.member_repository import MemberRepository
from app.repositories.invitation_repository import InvitationRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.security.api_keys import APIKeySecurity


class MemberService:
    @classmethod
    async def invite_member(
        cls,
        org_id: str,
        email: str,
        role: str,
        invited_by: str,
        expires_in_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        clean_email = email.strip().lower()

        # 1. Check if already an active member
        existing_user = await UserRepository.get_by_email(clean_email)
        if existing_user:
            existing_mem = await MemberRepository.get_by_user_id(org_id, existing_user["id"])
            if existing_mem and existing_mem.get("status") == "active":
                raise ConflictError(message=f"User '{clean_email}' is already a member of this organization", code="ALREADY_MEMBER")

        # 2. Cancel previous pending invitations for this email
        prev_pending = await InvitationRepository.get_pending_by_email(org_id, clean_email)
        if prev_pending:
            await InvitationRepository.update_status(prev_pending["id"], "cancelled")

        # 3. Generate secure token
        raw_token = secrets.token_urlsafe(32)
        token_hash = APIKeySecurity.hash_key(raw_token)

        days = expires_in_days or settings.INVITATION_EXPIRY_DAYS
        expires_at = datetime.now(timezone.utc) + timedelta(days=days)

        # 4. Create DB invitation
        inv = await InvitationRepository.create(
            org_id=org_id,
            email=clean_email,
            role=role,
            invited_by=invited_by,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        # 5. Audit log
        await AuditLogRepository.log_event(
            action="member.invited",
            resource_type="invitation",
            resource_id=inv["id"],
            organization_id=org_id,
            user_id=invited_by,
            metadata={"email": clean_email, "role": role},
        )

        inv_url = f"{settings.BASE_URL}/invitations/accept?token={raw_token}"
        inv["invitation_token"] = raw_token
        inv["invitation_url"] = inv_url
        return inv

    @classmethod
    async def resend_invitation(cls, invitation_id: str, org_id: str, user_id: str) -> Dict[str, Any]:
        inv = await InvitationRepository.get_by_id(invitation_id, org_id)
        if not inv:
            raise NotFoundError(message="Invitation not found", code="INVITATION_NOT_FOUND")

        raw_token = secrets.token_urlsafe(32)
        token_hash = APIKeySecurity.hash_key(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.INVITATION_EXPIRY_DAYS)

        # Update invitation with new token hash and extended expiry
        collection = InvitationRepository._collection()
        from bson import ObjectId
        await collection.update_one(
            {"_id": ObjectId(invitation_id)},
            {"$set": {
                "token_hash": token_hash,
                "expires_at": expires_at,
                "status": "pending",
                "created_at": datetime.now(timezone.utc),
            }}
        )

        inv["invitation_token"] = raw_token
        inv["invitation_url"] = f"{settings.BASE_URL}/invitations/accept?token={raw_token}"
        inv["expires_at"] = expires_at
        inv["status"] = "pending"
        return inv

    @classmethod
    async def cancel_invitation(cls, invitation_id: str, org_id: str, user_id: str) -> bool:
        inv = await InvitationRepository.get_by_id(invitation_id, org_id)
        if not inv:
            raise NotFoundError(message="Invitation not found", code="INVITATION_NOT_FOUND")

        await InvitationRepository.update_status(invitation_id, "cancelled")
        await AuditLogRepository.log_event(
            action="invitation.cancelled",
            resource_type="invitation",
            resource_id=invitation_id,
            organization_id=org_id,
            user_id=user_id,
        )
        return True

    @classmethod
    async def accept_invitation(
        cls,
        raw_token: str,
        name: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Dict[str, Any]:
        token_hash = APIKeySecurity.hash_key(raw_token)
        inv = await InvitationRepository.get_by_token_hash(token_hash)
        if not inv:
            raise NotFoundError(message="Invalid or unrecognized invitation token", code="INVALID_INVITATION_TOKEN")

        if inv.get("status") != "pending":
            raise ValidationError(message=f"Invitation is already {inv.get('status')}", code="INVITATION_NOT_PENDING")

        exp = inv.get("expires_at")
        if isinstance(exp, str):
            exp = datetime.fromisoformat(exp.replace("Z", "+00:00"))
        elif isinstance(exp, datetime) and exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp and exp < datetime.now(timezone.utc):
            await InvitationRepository.update_status(inv["id"], "expired")
            raise ValidationError(message="This invitation has expired", code="INVITATION_EXPIRED")

        org_id = str(inv["organization_id"])
        email = inv["email"]
        role = inv.get("role", "member")

        # 1. Resolve or create user
        user = await UserRepository.get_by_email(email)
        if not user:
            clean_name = name or email.split("@")[0].capitalize()
            raw_pwd = password or secrets.token_urlsafe(16)
            hashed_pwd = get_password_hash(raw_pwd)
            user = await UserRepository.create(
                name=clean_name,
                email=email,
                password_hash=hashed_pwd,
            )

        user_id = str(user["id"])

        # 2. Add or update membership in organization
        existing_mem = await MemberRepository.get_by_user_id(org_id, user_id)
        if existing_mem:
            await MemberRepository.update_member(existing_mem["id"], org_id, {
                "role": role,
                "status": "active",
                "joined_at": datetime.now(timezone.utc),
            })
        else:
            await MemberRepository.create_member(
                org_id=org_id,
                user_id=user_id,
                role=role,
                status="active",
            )

        # 3. Mark invitation as accepted
        now = datetime.now(timezone.utc)
        await InvitationRepository.update_status(inv["id"], "accepted", accepted_at=now)

        # 4. Audit event
        await AuditLogRepository.log_event(
            action="member.joined",
            resource_type="organization",
            resource_id=org_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={"invitation_id": inv["id"], "role": role},
        )

        # 5. Issue session tokens for immediate login
        access_token = create_access_token(user_id=user_id, org_id=org_id)
        refresh_token = create_refresh_token(user_id=user_id, org_id=org_id)

        return {
            "organization_id": org_id,
            "user": user,
            "role": role,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @classmethod
    async def list_members(
        cls,
        org_id: str,
        page: int = 1,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        return await MemberRepository.list_members(org_id=org_id, page=page, limit=limit, status=status)

    @classmethod
    async def list_invitations(cls, org_id: str) -> List[Dict[str, Any]]:
        return await InvitationRepository.list_invitations(org_id=org_id)

    @classmethod
    async def update_member(
        cls,
        member_id: str,
        org_id: str,
        actor_user_id: str,
        role: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        member = await MemberRepository.get_by_id(member_id, org_id)
        if not member:
            raise NotFoundError(message="Member not found", code="MEMBER_NOT_FOUND")

        # Owner protection: cannot demote last owner
        if member.get("role") == "owner" and role and role != "owner":
            owner_count = await MemberRepository.count_owners(org_id)
            if owner_count <= 1:
                raise ForbiddenError(
                    message="Cannot demote the only owner. Transfer organization ownership first.",
                    code="CANNOT_DEMOTE_LAST_OWNER",
                )

        updates: Dict[str, Any] = {}
        if role:
            updates["role"] = role
        if status:
            updates["status"] = status

        updated = await MemberRepository.update_member(member_id, org_id, updates)
        await AuditLogRepository.log_event(
            action="member.updated",
            resource_type="member",
            resource_id=member_id,
            organization_id=org_id,
            user_id=actor_user_id,
            metadata=updates,
        )
        return updated

    @classmethod
    async def remove_member(cls, member_id: str, org_id: str, actor_user_id: str) -> bool:
        member = await MemberRepository.get_by_id(member_id, org_id)
        if not member:
            raise NotFoundError(message="Member not found", code="MEMBER_NOT_FOUND")

        # Owner protection
        if member.get("role") == "owner":
            owner_count = await MemberRepository.count_owners(org_id)
            if owner_count <= 1:
                raise ForbiddenError(
                    message="Cannot remove the organization owner. Transfer ownership first.",
                    code="CANNOT_REMOVE_OWNER",
                )

        # Mark as removed (never physically erase to maintain audit trail)
        await MemberRepository.update_member(member_id, org_id, {"status": "removed"})
        await AuditLogRepository.log_event(
            action="member.removed",
            resource_type="member",
            resource_id=member_id,
            organization_id=org_id,
            user_id=actor_user_id,
            metadata={"removed_user_id": member["user_id"]},
        )
        return True

    @classmethod
    async def transfer_ownership(
        cls,
        org_id: str,
        current_owner_id: str,
        new_owner_user_id: str,
    ) -> Dict[str, Any]:
        org = await OrganizationRepository.get_by_id(org_id)
        if not org:
            raise NotFoundError(message="Organization not found", code="ORG_NOT_FOUND")

        if str(org["owner_id"]) != current_owner_id:
            raise ForbiddenError(message="Only the current organization owner can transfer ownership", code="NOT_ORG_OWNER")

        # Verify new owner is an active member
        new_member = await MemberRepository.get_by_user_id(org_id, new_owner_user_id)
        if not new_member or new_member.get("status") != "active":
            raise ValidationError(
                message="Target user must be an active member of this organization",
                code="TARGET_NOT_ACTIVE_MEMBER",
            )

        # Update org record
        await OrganizationRepository.update(org_id, {"owner_id": new_owner_user_id})

        # Demote current owner to admin
        current_mem = await MemberRepository.get_by_user_id(org_id, current_owner_id)
        if current_mem:
            await MemberRepository.update_member(current_mem["id"], org_id, {"role": "admin"})

        # Promote new user to owner
        await MemberRepository.update_member(new_member["id"], org_id, {"role": "owner"})

        await AuditLogRepository.log_event(
            action="organization.ownership_transferred",
            resource_type="organization",
            resource_id=org_id,
            organization_id=org_id,
            user_id=current_owner_id,
            metadata={"previous_owner": current_owner_id, "new_owner": new_owner_user_id},
        )

        return await OrganizationRepository.get_by_id(org_id)
