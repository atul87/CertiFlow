import pytest
import io
import csv
import zipfile
from datetime import datetime, timezone
from app.services.progress_service import ProgressService
from app.services.zip_service import sanitize_filename
from app.services.error_classifier import ErrorClassifier, ErrorCategory
from app.schemas.issuance import (
    JobStatus,
    ItemStatus,
    ZipStatus,
    IssuanceJobResponse,
    IssuanceItemResponse,
    ZipStatusResponse,
    ErrorRowItem,
)

pytestmark = pytest.mark.no_db


class TestIssuanceProgressCalculation:
    def test_zero_total_returns_zero(self):
        assert ProgressService.calculate_progress_percentage(0, 0, 0, 0) == 0.0

    def test_no_completed_returns_zero(self):
        assert ProgressService.calculate_progress_percentage(100, 0, 0, 0) == 0.0

    def test_halfway_completed(self):
        assert ProgressService.calculate_progress_percentage(100, 50, 0, 0) == 50.0

    def test_failed_items_count_towards_progress(self):
        # 50 completed + 10 failed out of 100 total = 60%
        # Ensures UI doesn't look stuck when failures occur
        pct = ProgressService.calculate_progress_percentage(100, 50, 10, 0)
        assert pct == 60.0

    def test_cancelled_items_count_towards_progress(self):
        # 40 completed + 10 failed + 50 cancelled out of 100 = 100%
        pct = ProgressService.calculate_progress_percentage(100, 40, 10, 50)
        assert pct == 100.0

    def test_full_completion(self):
        assert ProgressService.calculate_progress_percentage(5000, 5000, 0, 0) == 100.0

    def test_rounded_to_two_decimals(self):
        # 3480 completed + 12 failed out of 5000 = 3492/5000 = 69.84%
        pct = ProgressService.calculate_progress_percentage(5000, 3480, 12, 0)
        assert pct == 69.84

    def test_capped_at_hundred(self):
        pct = ProgressService.calculate_progress_percentage(100, 110, 0, 0)
        assert pct == 100.0


class TestFilenameSanitization:
    def test_standard_clean_name(self):
        filename = sanitize_filename("CERT-2026-000001", "Atul Kumar")
        assert filename == "CERT-2026-000001_Atul-Kumar.pdf"

    def test_path_traversal_protection(self):
        filename = sanitize_filename("CERT-01", "../../etc/passwd")
        assert "/" not in filename
        assert ".." not in filename
        assert "\\" not in filename
        assert filename.endswith(".pdf")
        assert "passwd" in filename

    def test_windows_reserved_characters_removed(self):
        # < > : " / \ | ? *
        filename = sanitize_filename('CERT:2026*01', 'Rahul "Super" Sharma?')
        for bad_char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
            assert bad_char not in filename
        assert filename.endswith(".pdf")

    def test_whitespace_and_empty_fallbacks(self):
        filename = sanitize_filename("", "")
        assert filename == "certificate_recipient.pdf"

        filename2 = sanitize_filename("CERT-99", "   ")
        assert filename2 == "CERT-99_recipient.pdf"


class TestErrorClassification:
    def test_permanent_errors(self):
        permanent_codes = [
            "MISSING_REQUIRED_FIELD",
            "INVALID_RECIPIENT_DATA",
            "FONT_NOT_FOUND",
            "TEMPLATE_NOT_PUBLISHED",
            "PERMISSION_DENIED",
            "INVALID_DATE",
        ]
        for code in permanent_codes:
            assert ErrorClassifier.classify(code) == ErrorCategory.PERMANENT
            assert not ErrorClassifier.is_retryable(code)

    def test_retryable_errors(self):
        retryable_codes = [
            "STORAGE_TIMEOUT",
            "STORAGE_ERROR",
            "REDIS_TIMEOUT",
            "RENDERER_CRASH",
            "DATABASE_TIMEOUT",
            "NETWORK_ERROR",
            "WORKER_TIMEOUT",
        ]
        for code in retryable_codes:
            assert ErrorClassifier.classify(code) == ErrorCategory.RETRYABLE
            assert ErrorClassifier.is_retryable(code)

    def test_keyword_heuristics_on_messages(self):
        assert ErrorClassifier.is_retryable("UNKNOWN", "Connection reset by peer")
        assert ErrorClassifier.is_retryable("UNKNOWN", "Database timed out")
        assert not ErrorClassifier.is_retryable("CUSTOM_CODE", "Missing required field 'student_name'")


class TestIssuanceSchemasAndEnums:
    def test_job_status_values(self):
        valid_statuses = {
            "draft", "queued", "starting", "processing",
            "paused", "completed", "completed_with_errors", "failed", "cancelled"
        }
        for s in valid_statuses:
            assert JobStatus(s) == s

    def test_item_status_values(self):
        valid_statuses = {"pending", "processing", "completed", "failed", "cancelled"}
        for s in valid_statuses:
            assert ItemStatus(s) == s

    def test_zip_status_values(self):
        valid_statuses = {"not_requested", "queued", "processing", "ready", "failed", "expired"}
        for s in valid_statuses:
            assert ZipStatus(s) == s

    def test_issuance_job_response_schema(self):
        now = datetime.now(timezone.utc)
        job_data = {
            "id": "60d5ec49f1b2c8b1f8e4e1a1",
            "organization_id": "60d5ec49f1b2c8b1f8e4e1a2",
            "template_id": "60d5ec49f1b2c8b1f8e4e1a3",
            "template_version_id": "60d5ec49f1b2c8b1f8e4e1a4",
            "import_id": "60d5ec49f1b2c8b1f8e4e1a5",
            "status": "processing",
            "total": 100,
            "pending": 40,
            "processing": 10,
            "completed": 48,
            "failed": 2,
            "cancelled": 0,
            "progress": 50.0,
            "created_by": "60d5ec49f1b2c8b1f8e4e1a6",
            "created_at": now,
        }
        resp = IssuanceJobResponse(**job_data)
        assert resp.total == 100
        assert resp.completed == 48
        assert resp.failed == 2
        assert resp.progress == 50.0

    def test_error_row_item_and_csv_generation(self):
        errors = [
            ErrorRowItem(
                row_number=42,
                recipient_name="Rahul",
                email="rahul@example.com",
                error_code="FONT_NOT_FOUND",
                error_message="Font Montserrat not loaded",
                attempts=3,
            ),
            ErrorRowItem(
                row_number=118,
                recipient_name="Priya",
                email="priya@example.com",
                error_code="MISSING_REQUIRED_FIELD",
                error_message="Field issue_date is missing",
                attempts=1,
            ),
        ]
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["row_number", "recipient_name", "email", "error_code", "error_message", "attempts"])
        for err in errors:
            writer.writerow([
                err.row_number,
                err.recipient_name,
                err.email,
                err.error_code,
                err.error_message,
                err.attempts,
            ])
        csv_text = output.getvalue()
        assert "row_number,recipient_name,email,error_code,error_message,attempts" in csv_text
        assert "42,Rahul,rahul@example.com,FONT_NOT_FOUND,Font Montserrat not loaded,3" in csv_text
        assert "118,Priya,priya@example.com,MISSING_REQUIRED_FIELD,Field issue_date is missing,1" in csv_text


class TestZipArchiveStreaming:
    def test_zip_in_memory_creation(self):
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("CERT-001_Atul-Kumar.pdf", b"%PDF-1.4 dummy pdf bytes 1")
            zf.writestr("CERT-002_Rahul-Sharma.pdf", b"%PDF-1.4 dummy pdf bytes 2")

        bio.seek(0)
        with zipfile.ZipFile(bio, mode="r") as zf:
            file_names = zf.namelist()
            assert "CERT-001_Atul-Kumar.pdf" in file_names
            assert "CERT-002_Rahul-Sharma.pdf" in file_names
            assert zf.read("CERT-001_Atul-Kumar.pdf") == b"%PDF-1.4 dummy pdf bytes 1"
