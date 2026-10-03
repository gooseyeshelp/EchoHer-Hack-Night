"""run_demo.py - prints the busy score and day metrics for each demo day."""
from demo_data import DEMO_DAYS
from busy_score import compute_day_summary


for name, (events, day) in DEMO_DAYS.items():
    s = compute_day_summary(events, day)
    bar = "#" * (s["busy_score"] // 5) + "-" * (20 - s["busy_score"] // 5)
    print("=" * 52)
    print(f"{name.upper()} DAY  ({s['date']})")
    print(f"  Events: {s['num_events']}   Busy: {s['busy_hours']}h   Free: {s['free_hours']}h")
    print(f"  Longest free block: {s['longest_free_block_hours']}h")
    print(f"  Busy score: [{bar}] {s['busy_score']}/100 ({s['busy_bucket']})")
print("=" * 52)
