import io
import pytest
import openpyxl
from app.core.exceptions import ValidationError
from app.services.excel_parser import ExcelParser


def create_dummy_xlsx() -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Students"
    ws.append(["Name", "Email Address", "Course", "Completion Date"])
    ws.append(["Atul Kumar", "atul@example.com", "Python Mastery", "2026-09-28"])
    ws.append(["Jane Doe", "jane@example.com", "Python Mastery", "2026-09-28"])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_parse_valid_xlsx():
    content = create_dummy_xlsx()
    headers, rows = ExcelParser.parse(content, "students.xlsx")
    assert headers == ["Name", "Email Address", "Course", "Completion Date"]
    assert len(rows) == 2
    assert rows[0]["Name"] == "Atul Kumar"
    assert rows[1]["Email Address"] == "jane@example.com"


def test_reject_macro_xlsm():
    content = create_dummy_xlsx()
    with pytest.raises(ValidationError) as exc:
        ExcelParser.parse(content, "macro_payload.xlsm")
    assert exc.value.code == "MACRO_EXCEL_PROHIBITED"
