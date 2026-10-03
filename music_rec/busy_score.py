from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo


# ---- Tunable knobs (tell your partner if you change these) ----
DAY_START = time(8, 0)    # start of "waking window"
DAY_END = time(22, 0)     # end of "waking window"
MAX_EVENTS = 8            # 8+ events counts as max "event load"
W_BUSY, W_COUNT, W_FRAG = 0.6, 0.2, 0.2   # score weights (sum to 1)


BUCKETS = [  # (upper bound inclusive, label)
    (20, "light"),
    (40, "easy"),
    (60, "moderate"),
    (80, "busy"),
    (100, "packed"),
]




def _parse(dt_str, tz):
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    return dt.astimezone(tz)




def _usable_intervals(events, win_start, win_end, tz):
    """Turn raw Google events into clipped (start, end) intervals inside the window."""
    out = []
    for ev in events:
        if ev.get("status") == "cancelled":
            continue
        # skip events the user declined
        if any(a.get("self") and a.get("responseStatus") == "declined"
               for a in ev.get("attendees", [])):
            continue
        s, e = ev.get("start", {}), ev.get("end", {})
        if "dateTime" not in s or "dateTime" not in e:
            continue  # all-day events have only "date" -> ignored
        start, end = _parse(s["dateTime"], tz), _parse(e["dateTime"], tz)
        start, end = max(start, win_start), min(end, win_end)  # clip to window
        if end > start:
            out.append((start, end))
    return out




def _merge(intervals):
    """Merge overlapping intervals so double-booked time isn't counted twice."""
    merged = []
    for s, e in sorted(intervals):
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged




def compute_day_summary(events, day=None, tz="America/Los_Angeles"):
    tzinfo = ZoneInfo(tz)
    day = day or datetime.now(tzinfo).date()
    win_start = datetime.combine(day, DAY_START, tzinfo)
    win_end = datetime.combine(day, DAY_END, tzinfo)
    window_min = (win_end - win_start).total_seconds() / 60


    raw = _usable_intervals(events, win_start, win_end, tzinfo)
    merged = _merge(raw)


    busy_min = sum((e - s).total_seconds() / 60 for s, e in merged)
    free_min = window_min - busy_min


    # free gaps: before first event, between events, after last event
    gaps, cursor = [], win_start
    for s, e in merged:
        gaps.append((s - cursor).total_seconds() / 60)
        cursor = e
    gaps.append((win_end - cursor).total_seconds() / 60)
    longest_free = max(gaps) if gaps else window_min


    busy_ratio = busy_min / window_min
    count_norm = min(len(raw) / MAX_EVENTS, 1.0)
    frag = 1 - (longest_free / window_min)  # small longest block -> more fragmented -> busier


    score = 100 * (W_BUSY * busy_ratio + W_COUNT * count_norm + W_FRAG * frag)
    score = max(0, min(100, round(score)))
    bucket = next(label for ub, label in BUCKETS if score <= ub)


    return {
        "date": day.isoformat(),
        "num_events": len(raw),
        "busy_hours": round(busy_min / 60, 2),
        "free_hours": round(free_min / 60, 2),
        "longest_free_block_hours": round(longest_free / 60, 2),
        "busy_score": score,          # 0-100  <- main thing for Partner B
        "busy_bucket": bucket,        # light / easy / moderate / busy / packed
    }




if __name__ == "__main__":
    import json
    demo = [
        {"start": {"dateTime": "2026-10-02T09:00:00-07:00"}, "end": {"dateTime": "2026-10-02T10:30:00-07:00"}},
        {"start": {"dateTime": "2026-10-02T10:00:00-07:00"}, "end": {"dateTime": "2026-10-02T11:00:00-07:00"}},  # overlaps
        {"start": {"dateTime": "2026-10-02T13:00:00-07:00"}, "end": {"dateTime": "2026-10-02T15:00:00-07:00"}},
        {"start": {"dateTime": "2026-10-02T16:00:00-07:00"}, "end": {"dateTime": "2026-10-02T17:00:00-07:00"}},
        {"start": {"date": "2026-10-02"}, "end": {"date": "2026-10-03"}},  # all-day, ignored
    ]
    print(json.dumps(compute_day_summary(demo, date(2026, 10, 2)), indent=2))



