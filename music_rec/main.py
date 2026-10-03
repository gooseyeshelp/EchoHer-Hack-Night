from demo_data import DEMO_DAYS
from busy_score import compute_day_summary
from song_rec import recommend_songs, get_music_targets

from user_profile import (
    FAVORITE_ARTISTS,
    FAVORITE_TRACKS
)


# Run the full pipeline for each demo calendar
for name, (events, day) in DEMO_DAYS.items():

    # -----------------------------
    # 1. CALCULATE BUSY SCORE
    # -----------------------------

    summary = compute_day_summary(
        events,
        day
    )

    busy_score = summary["busy_score"]


    # -----------------------------
    # 2. GET MUSIC TARGETS
    # -----------------------------

    energy, valence, danceability = (
        get_music_targets(busy_score)
    )


    # -----------------------------
    # 3. GET SONG RECOMMENDATIONS
    # -----------------------------

    recommendations = recommend_songs(
        busy_score,
        FAVORITE_ARTISTS,
        FAVORITE_TRACKS,
        top_n=10
    )


    # -----------------------------
    # 4. DISPLAY RESULTS
    # -----------------------------

    print("\n" + "=" * 60)

    print(
        f"{name.upper()} DAY "
        f"({summary['date']})"
    )

    print("=" * 60)

    print(
        f"Events: {summary['num_events']}"
    )

    print(
        f"Busy time: "
        f"{summary['busy_hours']}h"
    )

    print(
        f"Free time: "
        f"{summary['free_hours']}h"
    )

    print(
        f"Longest free block: "
        f"{summary['longest_free_block_hours']}h"
    )

    print(
        f"\nBusy score: "
        f"{busy_score}/100 "
        f"({summary['busy_bucket']})"
    )


    # -----------------------------
    # MUSIC PROFILE
    # -----------------------------

    print("\nMusic targets:")

    print(
        f"  Energy: "
        f"{energy:.2f}"
    )

    print(
        f"  Valence: "
        f"{valence:.2f}"
    )

    print(
        f"  Danceability: "
        f"{danceability:.2f}"
    )


    print(
        f"\nMusic mix: "
        f"{busy_score}% familiar / "
        f"{100 - busy_score}% discovery"
    )


    # -----------------------------
    # SONG LIST
    # -----------------------------

    print("\nYour soundtrack:\n")

    for i, (_, song) in enumerate(
        recommendations.iterrows(),
        start=1
    ):

        label = (
            "Familiar"
            if song["familiar"]
            else "Discovery"
        )

        print(
            f"{i}. "
            f"{song['track_name']} "
            f"— {song['artists']} "
            f"[{label}]"
        )


print("\n" + "=" * 60)