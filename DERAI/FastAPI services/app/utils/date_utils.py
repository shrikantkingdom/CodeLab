"""Date range utilities."""

from datetime import date, timedelta
from typing import Optional


def resolve_date_range(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    single_date: Optional[date] = None,
) -> tuple[date, date]:
    """Resolve date range from either a range or single date.

    Returns (start_date, end_date) tuple.
    If single_date is provided and range is not, uses single_date as both.
    If nothing is provided, defaults to last 30 days.
    """
    if date_from and date_to:
        return date_from, date_to
    if single_date:
        return single_date, single_date
    # Default: last 30 days
    today = date.today()
    return today - timedelta(days=30), today
