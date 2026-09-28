from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EmailAttachment(BaseModel):
    filename: str
    content: bytes
    content_type: str = "application/pdf"


class EmailMessage(BaseModel):
    to_email: str
    to_name: str = ""
    from_email: str
    from_name: str = ""
    reply_to: Optional[str] = None
    subject: str
    html_body: str = ""
    text_body: str = ""
    attachments: List[EmailAttachment] = []
    idempotency_key: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)

    def __init__(self, **data):
        # Support aliases html_content -> html_body, text_content -> text_body
        if "html_content" in data and "html_body" not in data:
            data["html_body"] = data.pop("html_content")
        if "text_content" in data and "text_body" not in data:
            data["text_body"] = data.pop("text_content")
        super().__init__(**data)


class SendResult(BaseModel):
    success: bool
    provider_message_id: Optional[str] = None
    provider: str = "email"
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retryable: bool = False

    @property
    def message_id(self) -> Optional[str]:
        return self.provider_message_id


class EmailProvider(ABC):
    provider_name: str = "base"

    @abstractmethod
    async def send_email(self, message: EmailMessage) -> SendResult:
        """Send an email and return normalized SendResult."""
        pass
