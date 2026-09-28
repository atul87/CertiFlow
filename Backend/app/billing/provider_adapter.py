from __future__ import annotations
from app.billing.base import BaseBillingProvider
from app.billing.mock_provider import MockBillingProvider
from app.core.config import settings


class BillingProviderAdapter:
    _provider_instance: BaseBillingProvider | None = None

    @classmethod
    def get_provider(cls) -> BaseBillingProvider:
        if cls._provider_instance is None:
            # Default to MockBillingProvider (can easily expand to Stripe / Razorpay)
            cls._provider_instance = MockBillingProvider()
        return cls._provider_instance
