import io
import csv
import re
from typing import List, Dict, Any, Tuple, Optional
from app.core.exceptions import ValidationError


class CSVParser:
    SUPPORTED_DELIMITERS = [",", ";", "\t", "|"]
    ENCODINGS_TO_TRY = ["utf-8-sig", "utf-8", "windows-1252", "latin-1"]

    @classmethod
    def detect_encoding(cls, content: bytes) -> str:
        """Attempt to decode content across standard encodings."""
        for enc in cls.ENCODINGS_TO_TRY:
            try:
                content.decode(enc)
                return enc
            except (UnicodeDecodeError, LookupError):
                continue
        return "utf-8"

    @classmethod
    def detect_delimiter(cls, text_sample: str) -> str:
        """Detect the CSV delimiter from the text sample."""
        if not text_sample:
            return ","

        lines = [line.strip() for line in text_sample.splitlines() if line.strip()][:10]
        if not lines:
            return ","

        # Try csv.Sniffer first
        try:
            sniffer = csv.Sniffer()
            sample_chunk = "\n".join(lines[:5])
            dialect = sniffer.sniff(sample_chunk, delimiters=";,|\t")
            if dialect.delimiter in cls.SUPPORTED_DELIMITERS:
                return dialect.delimiter
        except Exception:
            pass

        # Fallback: Count frequencies of supported delimiters across lines
        best_delimiter = ","
        max_consistency = -1

        for d in cls.SUPPORTED_DELIMITERS:
            counts = [line.count(d) for line in lines]
            if counts and counts[0] > 0 and len(set(counts)) == 1:
                # Delimiter appears the exact same number of times per line
                return d
            avg_count = sum(counts) / len(counts) if counts else 0
            if avg_count > max_consistency and avg_count > 0:
                max_consistency = avg_count
                best_delimiter = d

        return best_delimiter

    @classmethod
    def detect_header_row(cls, raw_rows: List[List[str]]) -> Tuple[int, List[str]]:
        """
        Identify the probable header row in the first 5 rows.
        Returns: (header_index, clean_column_names)
        """
        if not raw_rows:
            return 0, []

        best_index = 0
        max_score = -1

        for idx, row in enumerate(raw_rows[:5]):
            non_empty = [c.strip() for c in row if c and str(c).strip()]
            if not non_empty:
                continue

            # Header candidates are typically all non-numeric strings
            string_count = sum(1 for c in non_empty if not c.replace(".", "", 1).isdigit())
            score = string_count / len(non_empty) if non_empty else 0

            # Bonus score if common header names appear
            joined = " ".join(non_empty).lower()
            if any(k in joined for k in ["name", "email", "date", "course", "program", "id", "role", "title"]):
                score += 2.0

            if score > max_score:
                max_score = score
                best_index = idx

        # Generate unique sanitized column headers
        header_row = raw_rows[best_index]
        cleaned_headers: List[str] = []
        seen: Dict[str, int] = {}

        for i, col in enumerate(header_row):
            col_name = str(col).strip() if col is not None else ""
            if not col_name:
                col_name = f"Column_{i + 1}"

            if col_name in seen:
                seen[col_name] += 1
                col_name = f"{col_name}_{seen[col_name]}"
            else:
                seen[col_name] = 1

            cleaned_headers.append(col_name)

        return best_index, cleaned_headers

    @classmethod
    def parse(
        cls,
        content: bytes,
        max_rows: int = 50000
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Parse raw bytes of a CSV file.
        Returns: (columns, list_of_row_dicts)
        """
        encoding = cls.detect_encoding(content)
        try:
            text = content.decode(encoding)
        except Exception as e:
            raise ValidationError(message=f"Failed to decode CSV with {encoding}: {str(e)}", code="ENCODING_ERROR")

        delimiter = cls.detect_delimiter(text)

        reader = csv.reader(io.StringIO(text), delimiter=delimiter)
        raw_rows: List[List[str]] = []

        for row in reader:
            # Check if row is not completely empty
            if any(cell and str(cell).strip() for cell in row):
                raw_rows.append(row)
            if len(raw_rows) >= max_rows + 10:  # Safety guard
                break

        if not raw_rows:
            raise ValidationError(message="The uploaded CSV file is empty or contains no readable rows", code="EMPTY_FILE")

        header_idx, headers = cls.detect_header_row(raw_rows)
        data_rows = raw_rows[header_idx + 1:]

        results: List[Dict[str, Any]] = []
        for row in data_rows:
            row_dict: Dict[str, Any] = {}
            for col_idx, col_name in enumerate(headers):
                val = row[col_idx].strip() if col_idx < len(row) and row[col_idx] is not None else ""
                row_dict[col_name] = val
            results.append(row_dict)

        return headers, results
