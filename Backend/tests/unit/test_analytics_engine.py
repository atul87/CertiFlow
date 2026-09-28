"""
Unit tests for P7 Analytics Engine, Date Range Resolver, Signed URLs, and Reports.
Marked with @pytest.mark.no_db as these are pure logic/schema tests.
"""
from __future__ import annotations
import pytest
from datetime import datetime, timezone, timedelta

from app.services.analytics.date_range_helper import DateRangeHelper
from app.services.signed_url_service import SignedUrlService
from app.schemas.analytics import (
    KPICard,
    DashboardKPIs,
    StatusDistribution,
    ChartData,
    ChartDataset,
    UnifiedTimelineEvent,
    UnifiedCertificateTimelineResponse,
)
from app.schemas.reports import (
    ReportType,
    ReportFormat,
    ReportStatus,
    ReportJobCreateRequest,
)


@pytest.mark.no_db
def test_date_range_presets():
    """Verify all date range presets resolve correctly to valid UTC boundaries."""
    presets = [
        "today",
        "yesterday",
        "last_7_days",
        "last_30_days",
        "last_90_days",
        "this_month",
        "last_month",
        "this_year",
    ]
    for p in presets:
        start, end, prev_start, prev_end = DateRangeHelper.resolve_range(preset=p)
        assert start < end
        assert prev_start < prev_end
        assert end.tzinfo == timezone.utc
        assert start.tzinfo == timezone.utc


@pytest.mark.no_db
def test_custom_date_range():
    """Verify custom from/to date ranges are respected."""
    f = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    t = datetime(2026, 1, 15, 23, 59, 59, tzinfo=timezone.utc)
    start, end, prev_start, prev_end = DateRangeHelper.resolve_range(
        preset="custom",
        from_date=f,
        to_date=t,
    )
    assert start == f
    assert end == t
    # Previous period duration should match 15 days
    delta = end - start
    prev_delta = prev_end - prev_start
    assert abs(delta.total_seconds() - prev_delta.total_seconds()) < 10


@pytest.mark.no_db
def test_percentage_change_calculation():
    """Verify change percentage calculation under diverse conditions."""
    # Positive growth
    assert DateRangeHelper.calculate_change_percentage(120, 100) == 20.0
    # Negative growth
    assert DateRangeHelper.calculate_change_percentage(80, 100) == -20.0
    # Unchanged
    assert DateRangeHelper.calculate_change_percentage(100, 100) == 0.0
    # From zero previous
    assert DateRangeHelper.calculate_change_percentage(50, 0) == 100.0
    # Both zero
    assert DateRangeHelper.calculate_change_percentage(0, 0) == 0.0


@pytest.mark.no_db
def test_signed_url_token_lifecycle():
    """Verify HMAC token generation, validation, and expiration."""
    report_id = "rep_abcdef123456"
    token = SignedUrlService.generate_token(report_id, expires_in_seconds=60)
    assert token is not None
    assert isinstance(token, str)

    # Valid token
    assert SignedUrlService.verify_token(report_id, token) is True

    # Tampered token
    assert SignedUrlService.verify_token(report_id, token + "bad") is False
    assert SignedUrlService.verify_token("rep_different_id", token) is False

    # Expired token
    expired_token = SignedUrlService.generate_token(report_id, expires_in_seconds=-10)
    assert SignedUrlService.verify_token(report_id, expired_token) is False


@pytest.mark.no_db
def test_kpi_card_and_dashboard_schemas():
    """Verify Pydantic models for KPI cards and dashboard aggregations."""
    kpi = KPICard(value=12450, previous_value=10550, change_percentage=18.0)
    assert kpi.value == 12450
    assert kpi.change_percentage == 18.0

    kpis = DashboardKPIs(
        certificates_issued=kpi,
        active_certificates=KPICard(value=12000),
        revoked_certificates=KPICard(value=50),
        emails_sent=KPICard(value=11900),
        emails_delivered=KPICard(value=11500),
        delivery_rate=KPICard(value=96.6),
        verifications_successful=KPICard(value=8940),
        failed_operations=KPICard(value=12),
    )
    assert kpis.delivery_rate.value == 96.6


@pytest.mark.no_db
def test_chart_data_model():
    """Verify chart dataset and label contracts."""
    chart = ChartData(
        labels=["Sep 24", "Sep 25", "Sep 26"],
        datasets=[
            ChartDataset(name="Issued", values=[120, 240, 180]),
            ChartDataset(name="Delivered", values=[110, 230, 175]),
        ]
    )
    assert len(chart.labels) == 3
    assert len(chart.datasets) == 2
    assert chart.datasets[0].values == [120, 240, 180]


@pytest.mark.no_db
def test_unified_timeline_schemas():
    """Verify unified timeline schema contracts."""
    now = datetime.now(timezone.utc)
    ev = UnifiedTimelineEvent(
        type="email.delivered",
        title="Email Delivered",
        description="Delivered to recipient@example.com",
        timestamp=now,
        actor="Email Provider",
        metadata={"provider": "resend"},
    )
    tl = UnifiedCertificateTimelineResponse(
        certificate_id="cert_123",
        certificate_number="CERT-001",
        current_status="generated",
        events=[ev],
    )
    assert tl.certificate_id == "cert_123"
    assert len(tl.events) == 1
    assert tl.events[0].type == "email.delivered"


@pytest.mark.no_db
def test_report_create_request_validation():
    """Verify ReportJobCreateRequest defaults and options."""
    req = ReportJobCreateRequest(
        type=ReportType.CERTIFICATE_REPORT,
        format=ReportFormat.CSV,
        date_range="last_30_days",
    )
    assert req.type == "certificate_report"
    assert req.format == "csv"
    assert req.date_range == "last_30_days"
