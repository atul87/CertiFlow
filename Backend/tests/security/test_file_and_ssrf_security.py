import io
import zipfile
import pytest
from app.security.file_security import FileSecurity, MAGIC_BYTES
from app.security.webhooks import WebhookSecurity
from app.core.exceptions import ValidationError


def test_magic_bytes_validation():
    # Valid files
    assert FileSecurity.validate_magic_bytes(MAGIC_BYTES["png"] + b"payload", "png") is True
    assert FileSecurity.validate_magic_bytes(MAGIC_BYTES["jpeg"] + b"payload", "jpeg") is True
    assert FileSecurity.validate_magic_bytes(MAGIC_BYTES["pdf"] + b"payload", "pdf") is True
    assert FileSecurity.validate_magic_bytes(MAGIC_BYTES["zip"] + b"payload", "xlsx") is True
    assert FileSecurity.validate_magic_bytes(MAGIC_BYTES["woff"] + b"payload", "woff") is True
    assert FileSecurity.validate_magic_bytes(b"name,email,grade\nAlice,a@b.com,A", "csv") is True

    # Malicious files disguised with wrong extensions
    assert FileSecurity.validate_magic_bytes(b"MZ\x90\x00\x03\x00executable", "png") is False
    assert FileSecurity.validate_magic_bytes(b"\x7fELF\x02\x01\x01linux_bin", "jpeg") is False
    assert FileSecurity.validate_magic_bytes(b"<html><body>fake pdf</body></html>", "pdf") is False
    assert FileSecurity.validate_magic_bytes(b"MZ\x90\x00binary_in_csv", "csv") is False
    assert FileSecurity.validate_magic_bytes(b"not_a_zip", "xlsx") is False


def test_svg_script_detection():
    # Malicious SVG with embedded script
    malicious_svg = b"""
    <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
        <circle cx="50" cy="50" r="40" stroke="green" stroke-width="4" fill="yellow" />
        <script type="text/javascript">
            alert('XSS vulnerability execution');
        </script>
    </svg>
    """
    with pytest.raises(ValidationError) as exc:
        FileSecurity.sanitize_svg(malicious_svg)
    assert exc.value.code == "SVG_SCRIPT_DETECTED"


def test_svg_xxe_entity_injection_detection():
    # Malicious SVG with XXE XML entity expansion
    xxe_svg = b"""<?xml version="1.0" standalone="no"?>
    <!DOCTYPE svg [
      <!ELEMENT svg ANY >
      <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
    <svg width="200" height="200">&xxe;</svg>
    """
    with pytest.raises(ValidationError) as exc:
        FileSecurity.sanitize_svg(xxe_svg)
    assert exc.value.code == "SVG_XXE_DETECTED"


def test_svg_event_handler_and_foreign_object_stripping():
    # SVG with dangerous attributes and tags that should be stripped safely
    unsafe_svg = b"""
    <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
        <circle cx="50" cy="50" r="40" onload="alert('pwned')" onclick="fetch('/steal')" />
        <a href="javascript:alert(1)">Click me</a>
        <foreignObject width="100" height="50">
            <iframe src="https://evil.com"></iframe>
        </foreignObject>
    </svg>
    """
    cleaned = FileSecurity.sanitize_svg(unsafe_svg).decode("utf-8")
    assert "onload" not in cleaned
    assert "onclick" not in cleaned
    assert "foreignObject" not in cleaned
    assert "iframe" not in cleaned
    assert "javascript:" not in cleaned
    assert "<circle" in cleaned


def test_zip_slip_path_traversal_detection():
    # Create malicious in-memory ZIP with ../ path traversal
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../../etc/cron.d/malicious_cron", b"* * * * * root /bin/sh")
        zf.writestr("safe_report.csv", b"col1,col2\n1,2")
    
    zip_bytes = buf.getvalue()
    with pytest.raises(ValidationError) as exc:
        FileSecurity.validate_zip_archive(zip_bytes)
    assert exc.value.code == "ZIP_SLIP_ATTACK_DETECTED"


def test_zip_slip_windows_drive_letter():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("C:\\Windows\\System32\\calc.exe", b"malware")
    
    with pytest.raises(ValidationError) as exc:
        FileSecurity.validate_zip_archive(buf.getvalue())
    assert exc.value.code == "ZIP_SLIP_ATTACK_DETECTED"


def test_zip_safe_archive_passes():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("certificates/cert1.pdf", b"%PDF-dummy")
        zf.writestr("certificates/cert2.pdf", b"%PDF-dummy")
    
    members = FileSecurity.validate_zip_archive(buf.getvalue())
    assert len(members) == 2
    assert "certificates/cert1.pdf" in members


def test_ssrf_webhook_protection():
    # Loopback IP
    with pytest.raises(ValidationError) as exc:
        WebhookSecurity.validate_destination_url("http://127.0.0.1:8000/api/v1/certificates")
    assert exc.value.code == "WEBHOOK_SSRF_BLOCKED"

    # Localhost
    with pytest.raises(ValidationError) as exc:
        WebhookSecurity.validate_destination_url("http://localhost:3000/webhook")
    assert exc.value.code == "WEBHOOK_SSRF_BLOCKED"

    # Cloud metadata service IP (AWS/GCP)
    with pytest.raises(ValidationError) as exc:
        WebhookSecurity.validate_destination_url("http://169.254.169.254/latest/meta-data")
    assert exc.value.code == "WEBHOOK_SSRF_BLOCKED"

    # Non-HTTP protocol
    with pytest.raises(ValidationError) as exc:
        WebhookSecurity.validate_destination_url("gopher://127.0.0.1:6379/_flushall")
    assert exc.value.code == "INVALID_WEBHOOK_SCHEME"
