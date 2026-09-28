from __future__ import annotations
import uuid
import logging
from typing import List, Dict, Any, Optional
from app.providers.base import EmailProvider, EmailMessage, SendResult

logger = logging.getLogger(__name__)


class MockEmailProvider(EmailProvider):
    """
    Mock email provider for local development and automated testing.
    Records all sent messages in memory.
    """
    provider_name: str = "mock"
    sent_messages: List[EmailMessage] = []
    error_simulation: Optional[Dict[str, Any]] = None

    @classmethod
    def reset(cls):
        cls.sent_messages.clear()
        cls.error_simulation = None

    @classmethod
    def clear_sent_messages(cls):
        cls.sent_messages.clear()

    @classmethod
    def get_sent_messages(cls) -> List[EmailMessage]:
        return list(cls.sent_messages)

    @classmethod
    def simulate_error(
        cls,
        should_fail: bool,
        error_code: str = "SIMULATED_ERROR",
        error_message: str = "Simulated error",
        retryable: bool = False,
    ):
        if should_fail:
            cls.error_simulation = {
                "code": error_code,
                "message": error_message,
                "retryable": retryable,
            }
        else:
            cls.error_simulation = None

    async def send_email(self, message: EmailMessage) -> SendResult:
        if self.error_simulation:
            logger.warning("MockEmailProvider simulating error: %s", self.error_simulation)
            return SendResult(
                success=False,
                provider="mock",
                error_code=self.error_simulation.get("code", "MOCK_ERROR"),
                error_message=self.error_simulation.get("message", "Simulated error"),
                retryable=self.error_simulation.get("retryable", False),
            )

        msg_id = f"mock_{uuid.uuid4().hex[:12]}"
        self.sent_messages.append(message)
        logger.info("MockEmailProvider sent email to %s (subject: %s, msg_id: %s)", message.to_email, message.subject, msg_id)

        return SendResult(
            success=True,
            provider="mock",
            provider_message_id=msg_id,
        )
