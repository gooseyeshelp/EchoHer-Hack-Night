"""demo_data.py - fake university student days in Google Calendar event format."""
from datetime import date
from busy_score import compute_day_summary


TZ_OFFSET = "-07:00"  # Pacific daylight time; matches default tz in busy_score.py




def ev(day, start, end, title, desc=""):
    return {
        "summary": title,
        "description": desc,
        "start": {"dateTime": f"{day}T{start}:00{TZ_OFFSET}"},
        "end": {"dateTime": f"{day}T{end}:00{TZ_OFFSET}"},
    }




def all_day(day, title):
    return {"summary": title, "start": {"date": day}, "end": {"date": day}}




# Light day: Sunday
LIGHT = [
    all_day("2026-10-04", "Mom's birthday"),   # ignored
    ev("2026-10-04", "11:00", "12:00", "Brunch with roommates"),
    ev("2026-10-04", "16:00", "17:00", "Gym"),
]


# Typical weekday: Tuesday
TYPICAL = [
    ev("2026-10-06", "09:00", "10:30", "CS 61B Lecture", "Trees and graphs"),
    ev("2026-10-06", "11:00", "12:00", "MATH 54 Lecture"),
    ev("2026-10-06", "12:30", "13:15", "Lunch with study group"),
    ev("2026-10-06", "14:00", "16:00", "Chem Lab"),
    ev("2026-10-06", "17:00", "18:00", "Gym"),
    ev("2026-10-06", "19:30", "21:00", "Study session", "Problem set 4"),
]


# Packed day: Thursday, midterm week
PACKED = [
    all_day("2026-10-08", "Midterm week"),     # ignored
    ev("2026-10-08", "08:00", "09:30", "CS 61B Lecture"),
    ev("2026-10-08", "09:45", "11:00", "Office hours", "Ask about project 2"),
    ev("2026-10-08", "11:15", "12:30", "MATH 54 Midterm"),
    ev("2026-10-08", "12:30", "13:00", "Quick lunch"),
    ev("2026-10-08", "13:15", "15:00", "Chem Lab"),
    ev("2026-10-08", "15:15", "16:30", "Group project meeting"),
    ev("2026-10-08", "16:30", "17:30", "Club board meeting"),   # back to back
    ev("2026-10-08", "18:00", "19:00", "Part-time job shift"),
    ev("2026-10-08", "19:30", "21:30", "Cram for tomorrow's exam"),
]


DEMO_DAYS = {
    "light":   (LIGHT,   date(2026, 10, 4)),
    "typical": (TYPICAL, date(2026, 10, 6)),
    "packed":  (PACKED,  date(2026, 10, 8)),
}


if __name__ == "__main__":
    for name, (events, day) in DEMO_DAYS.items():
        s = compute_day_summary(events, day)
        print(f"{name:8s} score={s['busy_score']:3d} ({s['busy_bucket']}) "
              f"events={s['num_events']} busy={s['busy_hours']}h "
              f"longest_free={s['longest_free_block_hours']}h")



