from __future__ import annotations
import smtplib
import asyncio
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Optional
from app.providers.base import EmailProvider, EmailMessage, SendResult

logger = logging.getLogger(__name__)


class SMTPEmailProvider(EmailProvider):
    provider_name: str = "smtp"

    def __init__(
        self,
        host: str = "localhost",
        port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
        timeout: int = 30,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.timeout = timeout

    @staticmethod
    def _normalize_smtp_error(err_str: str) -> str:
        lower = err_str.lower()
        if "550" in err_str or "recipient" in lower or "unknown" in lower or "mailbox" in lower:
            return "EMAIL_INVALID_RECIPIENT"
        if "421" in err_str or "rate limit" in lower or "too many" in lower:
            return "EMAIL_PROVIDER_RATE_LIMIT"
        if "535" in err_str or "auth" in lower or "credential" in lower:
            return "EMAIL_PROVIDER_AUTH_FAILED"
        if "timeout" in lower or "timed out" in lower or "connection" in lower:
            return "EMAIL_PROVIDER_TIMEOUT"
        return "EMAIL_PROVIDER_REJECTED"

    def _sync_send(self, message: EmailMessage) -> SendResult:
        try:
            msg = MIMEMultipart("mixed")
            msg["Subject"] = message.subject
            msg["From"] = f"{message.from_name} <{message.from_email}>" if message.from_name else message.from_email
            msg["To"] = f"{message.to_name} <{message.to_email}>" if message.to_name else message.to_email
            if message.reply_to:
                msg["Reply-To"] = message.reply_to

            # Headers
            for k, v in message.headers.items():
                msg[k] = v

            # Alternative plain text + HTML parts
            body_alt = MIMEMultipart("alternative")
            if message.text_body:
                body_alt.attach(MIMEText(message.text_body, "plain", "utf-8"))
            if message.html_body:
                body_alt.attach(MIMEText(message.html_body, "html", "utf-8"))
            msg.attach(body_alt)

            # Attachments
            for att in message.attachments:
                part = MIMEApplication(att.content, _subtype="pdf")
                part.add_header("Content-Disposition", "attachment", filename=att.filename)
                msg.attach(part)

            # Send via SMTP
            server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
            if self.use_tls:
                server.starttls()
            if self.username and self.password:
                server.login(self.username, self.password)

            server.sendmail(message.from_email, [message.to_email], msg.as_string())
            server.quit()

            import uuid
            msg_id = f"smtp_{uuid.uuid4().hex[:12]}"
            return SendResult(success=True, provider="smtp", provider_message_id=msg_id)

        except smtplib.SMTPAuthenticationError as exc:
            return SendResult(
                success=False,
                provider="smtp",
                error_code="EMAIL_PROVIDER_AUTH_FAILED",
                error_message=f"SMTP Authentication failed: {exc}",
                retryable=False,
            )
        except smtplib.SMTPRecipientsRefused as exc:
            return SendResult(
                success=False,
                provider="smtp",
                error_code="EMAIL_INVALID_RECIPIENT",
                error_message=f"Recipient refused by SMTP server: {exc}",
                retryable=False,
            )
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, TimeoutError, OSError) as exc:
            return SendResult(
                success=False,
                provider="smtp",
                error_code="EMAIL_PROVIDER_TIMEOUT",
                error_message=f"SMTP connection timeout or error: {exc}",
                retryable=True,
            )
        except Exception as exc:
            err_code = self._normalize_smtp_error(str(exc))
            return SendResult(
                success=False,
                provider="smtp",
                error_code=err_code,
                error_message=f"SMTP sending error: {exc}",
                retryable=err_code in ("EMAIL_PROVIDER_TIMEOUT", "EMAIL_PROVIDER_RATE_LIMIT"),
            )

    async def send_email(self, message: EmailMessage) -> SendResult:
        return await asyncio.to_thread(self._sync_send, message)
