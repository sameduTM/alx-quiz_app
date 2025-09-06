"""Timezone utility functions for consistent datetime handling"""
from datetime import datetime, timezone


def utc_now():
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)


def make_aware(dt):
    """Convert naive datetime to UTC timezone-aware datetime"""
    if dt is None:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def ensure_utc(dt):
    """Ensure datetime is in UTC timezone"""
    if dt is None:
        return None

    if dt.tzinfo is None:
        # Assume naive datetime is already in UTC
        return dt.replace(tzinfo=timezone.utc)

    # Convert to UTC if not already
    return dt.astimezone(timezone.utc)


def seconds_between(start_dt, end_dt):
    """Calculate seconds between two datetimes, handling timezone issues"""
    start_aware = ensure_utc(start_dt)
    end_aware = ensure_utc(end_dt)

    if start_aware is None or end_aware is None:
        return 0

    return int((end_aware - start_aware).total_seconds())


def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    if seconds < 0:
        return "0:00"

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}:{minutes:02d}:{remaining_seconds:02d}"

    return f"{minutes}:{remaining_seconds:02d}"
