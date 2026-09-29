import pytest
import time
from app.core.exceptions import ValidationError
from app.services.email_render_service import EmailRenderService
from app.services.signed_url_service import SignedUrlService
from app.services.email_delivery_service import sanitize_filename
from app.providers.base import EmailMessage, EmailAttachment
from app.providers.mock import MockEmailProvider
from app.providers.smtp import SMTPEmailProvider
from app.repositories.email_settings_repository import EmailSettingsRepository


@pytest.mark.no_db
class TestEmailTemplateValidation:
    def test_extract_variables(self):
        text = "Hello {{recipient_name}}, your certificate {{certificate_number}} is ready!"
        vars_found = EmailRenderService.extract_variables(text)
        assert set(vars_found) == {"recipient_name", "certificate_number"}

    def test_validate_allowed_variables_success(self):
        text = "Hello {{recipient_name}}, your {{program_name}} certificate is at {{verification_url}}"
        vars_found = EmailRenderService.validate_template_variables(text)
        assert "recipient_name" in vars_found
        assert "program_name" in vars_found
        assert "verification_url" in vars_found

    def test_validate_unknown_variable_raises(self):
        text = "Hello {{student_full_name}}, congrats!"
        with pytest.raises(ValidationError) as exc_info:
            EmailRenderService.validate_template_variables(text)
        assert "student_full_name" in str(exc_info.value.message)


@pytest.mark.no_db
class TestEmailSecurityAndEscaping:
    def test_html_injection_escaping(self):
        template = {
            "subject": "Cert for {{recipient_name}}",
            "html_body": "<p>Hello {{recipient_name}}</p>",
            "text_body": "Hello {{recipient_name}}",
        }
        malicious_name = '<script>alert("hack")</script>'
        rendered = EmailRenderService.render_email(
            template_doc=template,
            recipient_data={"name": malicious_name},
            certificate_data={"certificate_number": "C-1"},
            organization_data={"name": "Org"},
            verification_url="https://example.com/verify/1",
            download_url="https://example.com/download/1",
        )
        assert "<script>" not in rendered["html"]
        assert "&lt;script&gt;" in rendered["html"]
        assert 'alert(&quot;hack&quot;)' in rendered["html"] or 'alert(&#x27;hack&#x27;)' in rendered["html"]

    def test_unicode_and_international_names(self):
        template = {
            "subject": "Certificate for {{recipient_name}}",
            "html_body": "<p>Namaste {{recipient_name}} 🎓</p>",
            "text_body": "Namaste {{recipient_name}} 🎓",
        }
        intl_name = "अतुल कुमार (Atul) 王伟 🌟"
        rendered = EmailRenderService.render_email(
            template_doc=template,
            recipient_data={"name": intl_name},
            certificate_data={"certificate_number": "CERT-IND-1"},
            organization_data={"name": "ग्लोबल एकेडमी"},
            verification_url="https://example.com/verify/ind1",
            download_url="https://example.com/download/ind1",
        )
        assert "अतुल कुमार" in rendered["html"]
        assert "王伟" in rendered["html"]
        assert "🌟" in rendered["html"]
        assert "अतुल कुमार" in rendered["subject"]

    def test_plain_text_generation(self):
        html = "<h1>Congratulations!</h1><p>You have earned <strong>Python Certificate</strong>.</p><a href='https://example.com'>Link</a>"
        text = EmailRenderService.generate_plain_text(html)
        assert "Congratulations!" in text
        assert "You have earned Python Certificate." in text
        assert "<h1>" not in text
        assert "<strong>" not in text


@pytest.mark.no_db
class TestSignedDownloadURLs:
    def test_generate_and_verify_valid_token(self):
        code = "CERT-XYZ-999"
        token = SignedUrlService.generate_token(code, expires_in_seconds=3600)
        assert token and "." in token

        is_valid = SignedUrlService.verify_token(code, token)
        assert is_valid is True

    def test_expired_token_fails(self):
        code = "CERT-EXPIRED"
        # -10 seconds in past
        token = SignedUrlService.generate_token(code, expires_in_seconds=-10)
        assert SignedUrlService.verify_token(code, token) is False

    def test_tampered_token_fails(self):
        code = "CERT-VALID"
        token = SignedUrlService.generate_token(code, expires_in_seconds=3600)
        tampered = token[:-4] + "abcd"
        assert SignedUrlService.verify_token(code, tampered) is False

    def test_wrong_code_fails(self):
        code = "CERT-ONE"
        token = SignedUrlService.generate_token(code, expires_in_seconds=3600)
        assert SignedUrlService.verify_token("CERT-TWO", token) is False


@pytest.mark.no_db
class TestFilenameSanitization:
    def test_path_traversal_sanitized(self):
        bad_name = "../../../etc/passwd.pdf"
        sanitized = sanitize_filename(bad_name)
        assert ".." not in sanitized
        assert "/" not in sanitized
        assert sanitized == "passwd.pdf"

    def test_spaces_and_special_chars_cleaned(self):
        raw = "Atul Kumar / Final * Cert!.pdf"
        sanitized = sanitize_filename(raw)
        assert " " not in sanitized
        assert "*" not in sanitized
        assert "!" not in sanitized
        assert sanitized.endswith(".pdf")


@pytest.mark.no_db
class TestEmailProviders:
    @pytest.mark.asyncio
    async def test_mock_email_provider_send(self):
        provider = MockEmailProvider()
        provider.clear_sent_messages()

        msg = EmailMessage(
            to_email="student@example.com",
            to_name="Student",
            from_name="Academy",
            from_email="academy@example.com",
            subject="Your Cert",
            html_content="<p>Cert</p>",
            text_content="Cert",
        )
        res = await provider.send_email(msg)
        assert res.success is True
        assert res.message_id.startswith("mock_")
        assert len(provider.get_sent_messages()) == 1

    @pytest.mark.asyncio
    async def test_mock_provider_simulated_failure(self):
        provider = MockEmailProvider()
        provider.simulate_error(True, error_code="SIMULATED_TIMEOUT", error_message="Timeout", retryable=True)
        try:
            msg = EmailMessage(
                to_email="test@example.com",
                to_name="Test",
                from_name="Academy",
                from_email="academy@example.com",
                subject="Subj",
                html_content="<p>Test</p>",
            )
            res = await provider.send_email(msg)
            assert res.success is False
            assert res.error_code == "SIMULATED_TIMEOUT"
            assert res.retryable is True
        finally:
            provider.simulate_error(False)

    def test_smtp_error_normalization(self):
        provider = SMTPEmailProvider()
        assert provider._normalize_smtp_error("550 User unknown") == "EMAIL_INVALID_RECIPIENT"
        assert provider._normalize_smtp_error("421 Service not available") == "EMAIL_PROVIDER_RATE_LIMIT"
        assert provider._normalize_smtp_error("535 Authentication credentials invalid") == "EMAIL_PROVIDER_AUTH_FAILED"
        assert provider._normalize_smtp_error("Connection timed out after 30s") == "EMAIL_PROVIDER_TIMEOUT"


@pytest.mark.no_db
class TestSettingsSecretMasking:
    def test_to_safe_response_masks_secrets(self):
        doc = {
            "organization_id": "507f1f77bcf86cd799439011",
            "provider": "smtp",
            "sender_name": "ABC Institute",
            "sender_email": "certs@example.com",
            "smtp_host": "smtp.mailgun.org",
            "smtp_port": 587,
            "smtp_username": "postmaster@abc.com",
            "smtp_password": "supersecretpassword123",
            "api_key": "resend_api_key_secret_xyz",
            "auto_email_on_issuance": True,
        }
        safe = EmailSettingsRepository.to_safe_response(doc, "507f1f77bcf86cd799439011")
        assert "supersecretpassword123" not in str(safe)
        assert "resend_api_key_secret_xyz" not in str(safe)
        assert safe["has_smtp_password"] is True
        assert safe["has_api_key"] is True
        assert safe["auto_email_on_issuance"] is True
