"""
timezone.py
-----------
Utility helpers for working with time zones.

This project uses Indian Standard Time (IST, Asia/Kolkata) for all
security audit timestamps so that fog + cloud logs match the operator's
local time.
"""

from datetime import datetime, timedelta, timezone

# IST is UTC+5:30 and does not observe daylight saving time.
IST_OFFSET = timedelta(hours=5, minutes=30)
IST_TZ = timezone(IST_OFFSET, name="Asia/Kolkata")


def now_ist() -> datetime:
    """
    Return a timezone-aware datetime in IST.
    """
    return datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(IST_TZ)


def now_ist_iso() -> str:
    """
    Return the current time in IST as an ISO-8601 string.
    Example: 2026-02-25T06:30:00+05:30
    """
    return now_ist().isoformat()

