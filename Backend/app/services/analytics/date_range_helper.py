from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional
import calendar


class DateRangeHelper:
    @classmethod
    def resolve_range(
        cls,
        preset: Optional[str] = "last_30_days",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Tuple[datetime, datetime, datetime, datetime]:
        """
        Resolves date range and corresponding previous comparison period.
        Returns: (start_date, end_date, prev_start, prev_end)
        """
        now = datetime.now(timezone.utc)

        if from_date and to_date:
            start = from_date if from_date.tzinfo else from_date.replace(tzinfo=timezone.utc)
            end = to_date if to_date.tzinfo else to_date.replace(tzinfo=timezone.utc)
            duration = end - start
            prev_end = start
            prev_start = start - duration
            return start, end, prev_start, prev_end

        p = (preset or "last_30_days").lower()

        if p == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
            prev_start = start - timedelta(days=1)
            prev_end = start

        elif p == "yesterday":
            end = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start = end - timedelta(days=1)
            prev_end = start
            prev_start = start - timedelta(days=1)

        elif p == "last_7_days":
            start = now - timedelta(days=7)
            end = now
            prev_end = start
            prev_start = start - timedelta(days=7)

        elif p == "last_30_days":
            start = now - timedelta(days=30)
            end = now
            prev_end = start
            prev_start = start - timedelta(days=30)

        elif p == "last_90_days":
            start = now - timedelta(days=90)
            end = now
            prev_end = start
            prev_start = start - timedelta(days=90)

        elif p == "this_month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
            # Previous month
            last_day_prev_month = start - timedelta(days=1)
            prev_start = last_day_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            prev_end = start

        elif p == "last_month":
            first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = first_of_this_month
            last_day_prev_month = first_of_this_month - timedelta(days=1)
            start = last_day_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            prev_end = start
            prev_last_day = start - timedelta(days=1)
            prev_start = prev_last_day.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        elif p == "this_year":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
            prev_start = start.replace(year=start.year - 1)
            prev_end = start

        else:
            # Default last 30 days
            start = now - timedelta(days=30)
            end = now
            prev_end = start
            prev_start = start - timedelta(days=30)

        return start, end, prev_start, prev_end

    @staticmethod
    def calculate_change_percentage(current: float | int, previous: float | int) -> float:
        """Calculate percentage delta between current period and previous period."""
        if previous == 0:
            if current == 0:
                return 0.0
            return 100.0 if current > 0 else -100.0

        diff = current - previous
        return round((diff / abs(previous)) * 100.0, 1)
