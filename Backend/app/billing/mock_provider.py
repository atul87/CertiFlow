from __future__ import annotations
import hmac
import hashlib
import json
import uuid
import secrets
from typing import Dict, Any, Optional
from app.billing.base import BaseBillingProvider
from app.core.config import settings


class MockBillingProvider(BaseBillingProvider):
    """
    Mock billing provider for robust local development, integration,
    and automated testing without external network dependencies.
    """
    @property
    def name(self) -> str:
        return "mock"

    async def create_customer(
        self,
        org_id: str,
        email: str,
        name: Optional[str] = None
    ) -> str:
        random_suffix = secrets.token_hex(8)
        return f"cus_mock_{random_suffix}"

    async def create_checkout_session(
        self,
        customer_id: str,
        plan_id: str,
        billing_interval: str,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        session_id = f"cs_mock_{secrets.token_hex(12)}"
        base_url = settings.APP_BASE_URL.rstrip("/")
        checkout_url = f"{base_url}/billing/checkout-mock?session_id={session_id}&plan={plan_id}&interval={billing_interval}"
        return {
            "checkout_url": checkout_url,
            "session_id": session_id,
            "provider": self.name
        }

    async def cancel_subscription(
        self,
        provider_subscription_id: str,
        immediate: bool = False
    ) -> bool:
        return True

    def calculate_signature(self, payload: bytes, secret: str) -> str:
        """Helper to generate valid signature for testing webhooks."""
        return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature_header: str,
        secret: str
    ) -> bool:
        if not signature_header or not secret:
            return False
        expected = self.calculate_signature(payload, secret)
        return hmac.compare_digest(expected, signature_header.strip())

    def parse_event(
        self,
        payload: bytes,
        signature_header: Optional[str] = None
    ) -> Dict[str, Any]:
        return json.loads(payload.decode("utf-8"))
