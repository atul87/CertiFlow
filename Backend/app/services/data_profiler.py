import re
from typing import List, Dict, Any
from dateutil import parser as date_parser

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
URL_REGEX = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)


class DataProfiler:
    @classmethod
    def infer_type(cls, values: List[str]) -> str:
        """Infer the data type of a column based on non-empty values."""
        non_empty = [v.strip() for v in values if v and str(v).strip()]
        if not non_empty:
            return "string"

        # Check sample size (up to 50 values)
        sample = non_empty[:50]

        # 1. Email check
        email_matches = sum(1 for v in sample if EMAIL_REGEX.match(v))
        if email_matches / len(sample) >= 0.7:
            return "email"

        # 2. URL check
        url_matches = sum(1 for v in sample if URL_REGEX.match(v))
        if url_matches / len(sample) >= 0.7:
            return "url"

        # 3. Numeric check
        num_matches = 0
        for v in sample:
            clean = v.replace(",", "").replace("$", "").replace("€", "").replace("₹", "").strip()
            try:
                float(clean)
                num_matches += 1
            except ValueError:
                pass
        if num_matches / len(sample) >= 0.8:
            return "number"

        # 4. Date check
        date_matches = 0
        for v in sample:
            if len(v) >= 4 and any(c.isdigit() for c in v):
                try:
                    date_parser.parse(v, fuzzy=False)
                    date_matches += 1
                except (ValueError, TypeError, OverflowError):
                    pass
        if date_matches / len(sample) >= 0.7:
            return "date"

        return "string"

    @classmethod
    def profile_columns(cls, columns: List[str], rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Produce data profiling metrics for every column in the dataset.
        """
        profiles: List[Dict[str, Any]] = []
        total_rows = len(rows)

        for idx, col in enumerate(columns):
            values = [str(r.get(col, "")).strip() for r in rows if r.get(col) is not None]
            non_empty_vals = [v for v in values if v]

            unique_vals = list(dict.fromkeys(non_empty_vals))
            samples = unique_vals[:5]

            inferred_type = cls.infer_type(non_empty_vals)

            profiles.append({
                "name": col,
                "index": idx,
                "sample_values": samples,
                "total_count": total_rows,
                "non_empty_count": len(non_empty_vals),
                "empty_count": total_rows - len(non_empty_vals),
                "unique_count": len(unique_vals),
                "detected_type": inferred_type
            })

        return profiles
