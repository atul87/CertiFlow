from __future__ import annotations
import re
import html
from typing import Dict, Any, List, Set, Optional
from app.core.exceptions import ValidationError

# Allowed template placeholder variables per P6.08
SUPPORTED_EMAIL_VARIABLES: Set[str] = {
    "recipient_name",
    "recipient_email",
    "certificate_number",
    "certificate_id",
    "verification_code",
    "verification_url",
    "certificate_status",
    "issued_at",
    "program_name",
    "course_name",
    "issuer_name",
    "issuer_website",
    "issuer_description",
    "download_url",
}

VARIABLE_REGEX = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


class EmailRenderService:
    @classmethod
    def extract_variables(cls, text: str) -> List[str]:
        """Extract all {{variable}} names found in text."""
        if not text:
            return []
        matches = VARIABLE_REGEX.findall(text)
        return sorted(list(set(matches)))

    @classmethod
    def validate_template_variables(cls, text: str) -> List[str]:
        """
        Validate that every placeholder variable is in the supported set.
        Raises ValidationError if an unsupported variable is found.
        Returns the list of found variables on success.
        """
        variables = cls.extract_variables(text)
        unknown = [v for v in variables if v not in SUPPORTED_EMAIL_VARIABLES]
        if unknown:
            raise ValidationError(
                message=f"Unsupported template variable(s): {', '.join(unknown)}. Allowed: {', '.join(sorted(SUPPORTED_EMAIL_VARIABLES))}",
                code="UNKNOWN_EMAIL_VARIABLE",
                details={"unsupported_variables": unknown},
            )
        return variables

    @classmethod
    def generate_plain_text(cls, html_text: str) -> str:
        """Generate a clean plain text fallback from an HTML string."""
        if not html_text:
            return ""
        # Replace block tags with newline
        text = re.sub(r"<\s*/?(h[1-6]|p|div|br|tr|li)[^>]*>", "\n", html_text, flags=re.IGNORECASE)
        # Strip remaining inline tags
        text = re.sub(r"<[^>]+>", "", text)
        # Unescape HTML entities
        text = html.unescape(text)
        # Normalize whitespace line by line
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
        return "\n".join([line for line in lines if line])

    @classmethod
    def render(
        cls,
        subject_template: str,
        html_template: str,
        text_template: str | None,
        context: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Render subject, HTML, and text with variables resolved.
        Applies HTML-escaping to prevent XSS / HTML injection in the HTML body.
        """
        # 1. Render Subject (plain text)
        def replace_subject(match):
            var_name = match.group(1)
            return str(context.get(var_name, ""))

        rendered_subject = VARIABLE_REGEX.sub(replace_subject, subject_template)

        # 2. Render HTML (escaped for security, preserving safe URLs)
        def replace_html(match):
            var_name = match.group(1)
            raw_val = str(context.get(var_name, ""))
            if var_name in ("verification_url", "download_url", "issuer_website"):
                # URL attributes: escape quotes and basic chars
                return html.escape(raw_val, quote=True)
            return html.escape(raw_val)

        rendered_html = VARIABLE_REGEX.sub(replace_html, html_template)

        # 3. Render Plain Text
        if text_template:
            def replace_text(match):
                var_name = match.group(1)
                return str(context.get(var_name, ""))

            rendered_text = VARIABLE_REGEX.sub(replace_text, text_template)
        else:
            rendered_text = cls.generate_plain_text(rendered_html)

        return {
            "subject": rendered_subject,
            "html": rendered_html,
            "text": rendered_text,
        }

    @classmethod
    def render_email(
        cls,
        template_doc: Dict[str, Any],
        recipient_data: Dict[str, Any],
        certificate_data: Dict[str, Any],
        organization_data: Dict[str, Any],
        verification_url: str,
        download_url: str,
    ) -> Dict[str, str]:
        """
        Convenience wrapper resolving all standard certificate email context.
        """
        cert_data = certificate_data.get("data", {})
        program = cert_data.get("program_name") or cert_data.get("course_name") or certificate_data.get("program_name", "")

        context: Dict[str, Any] = {
            "recipient_name": recipient_data.get("name") or recipient_data.get("recipient_name", ""),
            "recipient_email": recipient_data.get("email") or recipient_data.get("recipient_email", ""),
            "certificate_number": certificate_data.get("certificate_number", ""),
            "certificate_id": str(certificate_data.get("id", certificate_data.get("_id", ""))),
            "verification_code": certificate_data.get("verification_code", ""),
            "verification_url": verification_url,
            "certificate_status": certificate_data.get("status", "active"),
            "issued_at": str(certificate_data.get("created_at") or certificate_data.get("issued_at", "")),
            "program_name": program,
            "course_name": program,
            "issuer_name": organization_data.get("name", "Issuer"),
            "issuer_website": organization_data.get("website", ""),
            "issuer_description": organization_data.get("description", ""),
            "download_url": download_url,
        }

        return cls.render(
            subject_template=template_doc.get("subject", ""),
            html_template=template_doc.get("html_body", ""),
            text_template=template_doc.get("text_body"),
            context=context,
        )
