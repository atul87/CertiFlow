import pytest
from app.services.csv_parser import CSVParser


def test_detect_delimiters():
    # Comma
    assert CSVParser.detect_delimiter("Name,Email,Course\nAtul,a@b.com,Python") == ","
    # Semicolon
    assert CSVParser.detect_delimiter("Name;Email;Course\nAtul;a@b.com;Python") == ";"
    # Tab
    assert CSVParser.detect_delimiter("Name\tEmail\tCourse\nAtul\ta@b.com\tPython") == "\t"
    # Pipe
    assert CSVParser.detect_delimiter("Name|Email|Course\nAtul|a@b.com|Python") == "|"


def test_detect_encoding():
    utf8_bytes = "Name,Email\nAtul,atul@example.com".encode("utf-8")
    assert CSVParser.detect_encoding(utf8_bytes) in ["utf-8", "utf-8-sig"]

    bom_bytes = b"\xef\xbb\xbfName,Email\nAtul,atul@example.com"
    assert CSVParser.detect_encoding(bom_bytes) == "utf-8-sig"


def test_header_detection_with_preamble():
    raw_rows = [
        ["Annual Workshop Recipient List 2026", "", ""],
        ["Student Name", "Email Address", "Completion Date"],
        ["Atul Kumar", "atul@example.com", "2026-09-28"]
    ]
    idx, headers = CSVParser.detect_header_row(raw_rows)
    assert idx == 1
    assert headers == ["Student Name", "Email Address", "Completion Date"]


def test_parse_csv_strips_empty_rows():
    csv_text = """
Name,Email,Course
Atul Kumar,atul@example.com,Python

Rahul Sharma,rahul@example.com,Python
, , 
Priya Singh,priya@example.com,Python
    """
    headers, rows = CSVParser.parse(csv_text.strip().encode("utf-8"))
    assert headers == ["Name", "Email", "Course"]
    assert len(rows) == 3
    assert rows[0]["Name"] == "Atul Kumar"
    assert rows[1]["Name"] == "Rahul Sharma"
    assert rows[2]["Name"] == "Priya Singh"
