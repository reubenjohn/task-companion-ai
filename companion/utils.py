from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def datetime_from_utc_to_local(utc_datetime_ms: int, timezone_name: str) -> datetime:
    return datetime.fromtimestamp(utc_datetime_ms / 1000, timezone.utc).astimezone(
        ZoneInfo(timezone_name)
    )
