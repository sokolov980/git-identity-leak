from datetime import datetime
from schemas import Signal

def analyze_temporal(signals: list[Signal]):
    """
    Extract activity windows and timezone stability from timestamps.
    """
    timestamps = []
    for s in signals:
        if s.first_seen:
            timestamps.append(datetime.fromisoformat(s.first_seen))
        if s.last_seen:
            timestamps.append(datetime.fromisoformat(s.last_seen))
    if not timestamps:
        return {}

    earliest = min(timestamps)
    latest = max(timestamps)
    duration_days = (latest - earliest).days

    return {
        "earliest_seen": earliest.isoformat(),
        "latest_seen": latest.isoformat(),
        "duration_days": duration_days
    }
