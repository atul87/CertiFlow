from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseBillingProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name e.g. 'mock', 'stripe', 'razorpay'."""
        pass

    @abstractmethod
    async def create_customer(
        self,
        org_id: str,
        email: str,
        name: Optional[str] = None
    ) -> str:
        """Create a billing customer and return provider customer ID."""
        pass

    @abstractmethod
    async def create_checkout_session(
        self,
        customer_id: str,
        plan_id: str,
        billing_interval: str,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Create a checkout session for subscription purchase/upgrade.
        Returns: {'checkout_url': str, 'session_id': str}
        """
        pass

    @abstractmethod
    async def cancel_subscription(
        self,
        provider_subscription_id: str,
        immediate: bool = False
    ) -> bool:
        """Cancel subscription with provider."""
        pass

    @abstractmethod
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature_header: str,
        secret: str
    ) -> bool:
        """Verify authenticity of incoming webhook message."""
        pass

    @abstractmethod
    def parse_event(
        self,
        payload: bytes,
        signature_header: Optional[str] = None
    ) -> Dict[str, Any]:
        """Parse raw webhook into normalized event dictionary."""
        pass
