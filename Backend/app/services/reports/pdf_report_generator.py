from __future__ import annotations
import io
from datetime import datetime, timezone
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.organization_repository import OrganizationRepository


class PDFReportGenerator:
    @classmethod
    async def generate_summary_pdf(
        cls,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> bytes:
        org = await OrganizationRepository.get_by_id(org_id) or {"name": "Organization"}
        org_name = org.get("name", "Organization")

        kpis = await AnalyticsRepository.get_kpis(org_id, start_date, end_date)
        templates_breakdown = await AnalyticsRepository.get_issuance_by_template(org_id, start_date, end_date)
        programs_breakdown = await AnalyticsRepository.get_issuance_by_program(org_id, start_date, end_date)
        email_stats = await AnalyticsRepository.get_email_analytics(org_id, start_date, end_date)
        verif_stats = await AnalyticsRepository.get_verification_analytics(org_id, start_date, end_date)

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=15,
        )
        h2_style = ParagraphStyle(
            "Heading2",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=14,
            spaceAfter=8,
        )
        cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#334155"),
        )
        header_cell_style = ParagraphStyle(
            "TableHeaderCell",
            parent=styles["Normal"],
            fontSize=10,
            leading=13,
            textColor=colors.white,
            fontName="Helvetica-Bold",
        )

        elements = []

        # 1. Header
        elements.append(Paragraph(f"Executive Analytics Report", title_style))
        period_str = f"Organization: <b>{org_name}</b> | Period: {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
        elements.append(Paragraph(period_str, subtitle_style))
        elements.append(Spacer(1, 10))

        # 2. Executive Summary KPIs Table
        elements.append(Paragraph("1. Key Performance Indicators", h2_style))
        kpi_data = [
            [
                Paragraph("Metric", header_cell_style),
                Paragraph("Value", header_cell_style),
                Paragraph("Metric", header_cell_style),
                Paragraph("Value", header_cell_style),
            ],
            [
                Paragraph("Certificates Issued", cell_style),
                Paragraph(str(kpis.get("certificates_issued", 0)), cell_style),
                Paragraph("Emails Sent", cell_style),
                Paragraph(str(email_stats.get("sent", 0)), cell_style),
            ],
            [
                Paragraph("Active Certificates", cell_style),
                Paragraph(str(kpis.get("active_certificates", 0)), cell_style),
                Paragraph("Emails Delivered", cell_style),
                Paragraph(str(email_stats.get("delivered", 0)), cell_style),
            ],
            [
                Paragraph("Revoked Certificates", cell_style),
                Paragraph(str(kpis.get("revoked_certificates", 0)), cell_style),
                Paragraph("Delivery Rate", cell_style),
                Paragraph(f"{email_stats.get('delivery_rate', 0.0)}%", cell_style),
            ],
            [
                Paragraph("Successful Verifications", cell_style),
                Paragraph(str(verif_stats.get("successful_valid", 0)), cell_style),
                Paragraph("Failed Operations", cell_style),
                Paragraph(str(kpis.get("failed_operations", 0)), cell_style),
            ],
        ]

        t_kpi = Table(kpi_data, colWidths=[150, 115, 150, 115])
        t_kpi.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(t_kpi)
        elements.append(Spacer(1, 15))

        # 3. Issuance Breakdown by Program Table
        elements.append(Paragraph("2. Program Issuance Breakdown", h2_style))
        prog_rows = [
            [
                Paragraph("Program / Course Name", header_cell_style),
                Paragraph("Certificates Issued", header_cell_style),
            ]
        ]
        if programs_breakdown:
            for p in programs_breakdown[:8]:
                prog_rows.append([
                    Paragraph(p["program_name"], cell_style),
                    Paragraph(str(p["count"]), cell_style),
                ])
        else:
            prog_rows.append([Paragraph("No program issuance recorded in this period", cell_style), Paragraph("0", cell_style)])

        t_prog = Table(prog_rows, colWidths=[380, 150])
        t_prog.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(t_prog)
        elements.append(Spacer(1, 15))

        # 4. Verification Summary
        elements.append(Paragraph("3. Verification & Trust Metrics", h2_style))
        verif_rows = [
            [
                Paragraph("Total Attempts", header_cell_style),
                Paragraph("Valid", header_cell_style),
                Paragraph("Revoked", header_cell_style),
                Paragraph("Expired / Invalid", header_cell_style),
            ],
            [
                Paragraph(str(verif_stats.get("total_attempts", 0)), cell_style),
                Paragraph(str(verif_stats.get("successful_valid", 0)), cell_style),
                Paragraph(str(verif_stats.get("revoked", 0)), cell_style),
                Paragraph(str(verif_stats.get("not_found_or_invalid", 0) + verif_stats.get("expired", 0)), cell_style),
            ]
        ]
        t_verif = Table(verif_rows, colWidths=[132, 132, 133, 133])
        t_verif.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#059669")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(t_verif)

        # Build document
        doc.build(elements)
        return buf.getvalue()
