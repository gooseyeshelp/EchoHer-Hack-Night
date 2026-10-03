import pandas as pd
from pathlib import Path


# LOAD SONG DATABASE

dataset_path = Path(__file__).parent / "dataset.csv"

songs = pd.read_csv(dataset_path)

songs = songs.drop_duplicates(
    subset=["track_name", "artists"]
)

songs = songs.dropna(
    subset=[
        "track_name",
        "artists",
        "energy",
        "valence",
        "danceability",
        "popularity"
    ]
)


# CALENDAR -> MUSIC CHARACTERISTICS

def get_music_targets(busy_score):

    busy_score = max(0, min(100, busy_score))

    # Busy day -> calmer music
    # Light day -> more energetic music

    target_energy = (
        0.90 - (busy_score / 100) * 0.60
    )

    target_valence = (
        0.80 - (busy_score / 100) * 0.35
    )

    target_danceability = (
        0.85 - (busy_score / 100) * 0.35
    )

    return (
        target_energy,
        target_valence,
        target_danceability
    )


# MARK FAMILIAR MUSIC

def mark_familiar(
    data,
    favorite_artists,
    favorite_tracks
):

    data = data.copy()

    favorite_artists = {
        artist.lower().strip()
        for artist in favorite_artists
    }

    favorite_tracks = {
        track.lower().strip()
        for track in favorite_tracks
    }

    def artist_is_familiar(artist_string):

        artists = {
            artist.strip()
            for artist
            in artist_string.lower().split(";")
        }

        return bool(
            artists & favorite_artists
        )

    data["artist_familiar"] = (
        data["artists"]
        .apply(artist_is_familiar)
    )

    data["track_familiar"] = (
        data["track_name"]
        .str.lower()
        .str.strip()
        .isin(favorite_tracks)
    )

    # For the demo, familiarity is based on
    # whether the user already listens to the artist.
    data["familiar"] = data["artist_familiar"]

    return data


# SCORE MUSIC CHARACTERISTICS

def score_music(data, busy_score):

    data = data.copy()

    (
        target_energy,
        target_valence,
        target_danceability
    ) = get_music_targets(busy_score)

    data["energy_match"] = (
        1 - abs(
            data["energy"]
            - target_energy
        )
    )

    data["valence_match"] = (
        1 - abs(
            data["valence"]
            - target_valence
        )
    )

    data["danceability_match"] = (
        1 - abs(
            data["danceability"]
            - target_danceability
        )
    )

    data["popularity_score"] = (
        data["popularity"] / 100
    )

    data["score"] = (
        0.40 * data["energy_match"]
        + 0.20 * data["valence_match"]
        + 0.20 * data["danceability_match"]
        + 0.20 * data["popularity_score"]
    )

    return data


# MAIN RECOMMENDATION FUNCTION

def recommend_songs(
    busy_score,
    favorite_artists,
    favorite_tracks,
    top_n=10
):

    recommendations = mark_familiar(
        songs,
        favorite_artists,
        favorite_tracks
    )

    recommendations = score_music(
        recommendations,
        busy_score
    )


    # FAMILIAR VS DISCOVERY
    # Busier day -> more familiar artists
    # Lighter day -> more discovery artists

    familiar_ratio = busy_score / 100

    familiar_count = round(
        top_n * familiar_ratio
    )

    discovery_count = (
        top_n - familiar_count
    )


    # FAMILIAR SONGS

    familiar = recommendations[
        recommendations["familiar"]
    ]

    familiar = familiar.sort_values(
        "score",
        ascending=False
    )

    familiar = familiar.head(
        familiar_count
    )


    # DISCOVERY SONGS

    discovery = recommendations[
        ~recommendations["familiar"]
    ]

    discovery = discovery.sort_values(
        "score",
        ascending=False
    )

    discovery = discovery.head(
        discovery_count
    )


    # COMBINE RESULTS

    final = pd.concat(
        [familiar, discovery]
    )

    # Shuffle so familiar/discovery
    # aren't shown in separate chunks

    final = final.sample(
        frac=1,
        random_state=42
    )


    return final[
        [
            "track_name",
            "artists",
            "energy",
            "valence",
            "danceability",
            "popularity",
            "familiar",
            "score"
        ]
    ]


# TEST

if __name__ == "__main__":

    from user_profile import (
        FAVORITE_ARTISTS,
        FAVORITE_TRACKS
    )

    busy_score = 80

    recommendations = recommend_songs(
        busy_score,
        FAVORITE_ARTISTS,
        FAVORITE_TRACKS
    )

    print(
        "\nBUSY SCORE:",
        busy_score
    )

    print(
        f"FAMILIAR: {busy_score}%"
    )

    print(
        f"DISCOVERY: {100 - busy_score}%"
    )

    print(
        "\nRECOMMENDED SONGS:\n"
    )

    print(
        recommendations.to_string(
            index=False
        )
    )