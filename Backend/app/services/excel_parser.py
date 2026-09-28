import io
from datetime import datetime, date
from typing import List, Dict, Any, Tuple
import openpyxl
from app.core.exceptions import ValidationError
from app.services.csv_parser import CSVParser


class ExcelParser:
    @classmethod
    def parse(
        cls,
        content: bytes,
        filename: str,
        max_rows: int = 50000
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Parse raw bytes of an Excel (.xlsx, .xls) workbook in memory.
        Returns: (columns, list_of_row_dicts)
        """
        lower_name = filename.lower()
        if lower_name.endswith(".xlsm"):
            raise ValidationError(
                message="Macro-enabled Excel files (.xlsm) are not permitted for security reasons.",
                code="MACRO_EXCEL_PROHIBITED"
            )

        try:
            wb = openpyxl.load_workbook(
                filename=io.BytesIO(content),
                read_only=True,
                data_only=True
            )
        except Exception as e:
            raise ValidationError(message=f"Failed to open Excel workbook: {str(e)}", code="INVALID_EXCEL_FILE")

        sheet = wb.active
        if not sheet:
            raise ValidationError(message="Excel workbook contains no active worksheets", code="EMPTY_EXCEL_FILE")

        raw_rows: List[List[str]] = []
        for row in sheet.iter_rows(values_only=True):
            cleaned_row = []
            has_val = False
            for cell in row:
                if cell is None:
                    cleaned_row.append("")
                elif isinstance(cell, (datetime, date)):
                    cleaned_row.append(cell.strftime("%Y-%m-%d"))
                    has_val = True
                else:
                    s_val = str(cell).strip()
                    cleaned_row.append(s_val)
                    if s_val:
                        has_val = True

            if has_val:
                raw_rows.append(cleaned_row)

            if len(raw_rows) >= max_rows + 10:
                break

        wb.close()

        if not raw_rows:
            raise ValidationError(message="Excel sheet contains no data rows", code="EMPTY_EXCEL_FILE")

        # Detect headers using CSVParser's detection heuristic
        header_idx, headers = CSVParser.detect_header_row(raw_rows)
        data_rows = raw_rows[header_idx + 1:]

        results: List[Dict[str, Any]] = []
        for row in data_rows:
            row_dict: Dict[str, Any] = {}
            for col_idx, col_name in enumerate(headers):
                val = row[col_idx] if col_idx < len(row) else ""
                row_dict[col_name] = val
            results.append(row_dict)

        return headers, results
