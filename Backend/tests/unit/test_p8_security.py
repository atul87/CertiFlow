import pytest
import time
from datetime import datetime, timezone

from app.core.permissions import (
    PERMISSIONS,
    SYSTEM_ROLE_PERMISSIONS,
    API_SCOPE_PERMISSIONS,
    get_role_permissions,
)
from app.core.exceptions import ValidationError
from app.security.api_keys import APIKeySecurity
from app.security.webhooks import WebhookSecurity


@pytest.mark.no_db
class TestP8SecurityUnit:
    def test_api_key_generation_and_hashing(self):
        raw_key, key_hash, prefix = APIKeySecurity.generate_api_key(is_test=False)
        assert raw_key.startswith("ck_live_")
        assert len(raw_key) > 30
        assert prefix.startswith("ck_live_")
        assert len(key_hash) == 64  # SHA-256 hex digest

        # Verify hash repeatability
        assert APIKeySecurity.hash_key(raw_key) == key_hash

        # Test key format
        raw_test_key, test_hash, test_prefix = APIKeySecurity.generate_api_key(is_test=True)
        assert raw_test_key.startswith("ck_test_")
        assert test_prefix.startswith("ck_test_")

    def test_webhook_secret_and_hmac_signatures(self):
        secret = WebhookSecurity.generate_secret()
        assert secret.startswith("whsec_")
        assert len(secret) > 20

        secret_hash = WebhookSecurity.hash_secret(secret)
        assert len(secret_hash) == 64

        body = b'{"event":"certificate.generated","data":{"id":"123"}}'
        timestamp = str(int(time.time()))

        sig = WebhookSecurity.calculate_signature(secret, timestamp, body)
        assert len(sig) == 64

        # Valid signature verification
        is_valid = WebhookSecurity.verify_signature(
            secret=secret,
            signature=sig,
            timestamp=timestamp,
            payload=body,
            max_age_seconds=300,
        )
        assert is_valid is True

        # Tampered body fails
        tampered_body = b'{"event":"certificate.generated","data":{"id":"999"}}'
        assert WebhookSecurity.verify_signature(
            secret=secret,
            signature=sig,
            timestamp=timestamp,
            payload=tampered_body,
        ) is False

        # Expired timestamp fails
        old_timestamp = str(int(time.time()) - 400)
        old_sig = WebhookSecurity.calculate_signature(secret, old_timestamp, body)
        assert WebhookSecurity.verify_signature(
            secret=secret,
            signature=old_sig,
            timestamp=old_timestamp,
            payload=body,
            max_age_seconds=300,
        ) is False

    def test_ssrf_url_validation(self):
        # Public HTTPS URLs must pass
        valid_url = WebhookSecurity.validate_destination_url("https://api.customer.com/webhooks")
        assert valid_url == "https://api.customer.com/webhooks"

        # Private and loopback target IPs must be blocked
        with pytest.raises(ValidationError) as exc:
            WebhookSecurity.validate_destination_url("http://127.0.0.1:8000/hook")
        assert "private" in str(exc.value).lower() or "loopback" in str(exc.value).lower()

        with pytest.raises(ValidationError) as exc:
            WebhookSecurity.validate_destination_url("http://localhost/hook")
        assert "private" in str(exc.value).lower() or "loopback" in str(exc.value).lower()

        with pytest.raises(ValidationError) as exc:
            WebhookSecurity.validate_destination_url("http://169.254.169.254/latest/meta-data")
        assert "private" in str(exc.value).lower() or "metadata" in str(exc.value).lower()

        with pytest.raises(ValidationError) as exc:
            WebhookSecurity.validate_destination_url("http://10.0.0.5/api")
        assert "private" in str(exc.value).lower() or "loopback" in str(exc.value).lower()

    def test_permission_registry_and_role_mappings(self):
        # All system roles must map to recognized permissions
        for role, perms in SYSTEM_ROLE_PERMISSIONS.items():
            assert perms.issubset(PERMISSIONS), f"Role {role} contains unregistered permissions: {perms - PERMISSIONS}"

        # Owner must have all permissions
        owner_perms = get_role_permissions("owner")
        assert owner_perms == PERMISSIONS

        # Admin must have members and certificates management but not ownership transfer
        admin_perms = get_role_permissions("admin")
        assert "certificates.create" in admin_perms
        assert "members.invite" in admin_perms

        # Viewer has only read permissions
        viewer_perms = get_role_permissions("viewer")
        for p in viewer_perms:
            assert p.endswith(".read") or p.endswith(".download"), f"Viewer has non-read permission: {p}"

        # API scope mapping check
        for scope, mapped_perms in API_SCOPE_PERMISSIONS.items():
            assert mapped_perms.issubset(PERMISSIONS), f"Scope {scope} maps to unregistered permissions"
