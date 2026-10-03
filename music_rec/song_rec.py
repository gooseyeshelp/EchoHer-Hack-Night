import pandas as pd
from pathlib import Path


# -----------------------------
# LOAD DATA
# -----------------------------

dataset_path = Path(__file__).parent / "dataset.csv"
songs = pd.read_csv(dataset_path)

# Clean dataset
songs = songs.drop_duplicates(subset=["track_name", "artists"])

songs = songs.dropna(
    subset=[
        "track_name",
        "artists",
        "track_genre",
        "energy",
        "valence",
        "danceability"
    ]
)


# -----------------------------
# BUSY SCORE -> MUSIC TARGETS
# -----------------------------

def get_music_targets(busy_score):

    # Keep busy score between 0 and 100
    busy_score = max(0, min(100, busy_score))

    # Busier day -> more energetic music
    target_energy = 0.30 + (busy_score / 100) * 0.60

    # Busier day -> slightly more upbeat music
    target_valence = 0.45 + (busy_score / 100) * 0.30

    # Busier day -> somewhat more danceable music
    target_danceability = 0.45 + (busy_score / 100) * 0.35

    return target_energy, target_valence, target_danceability


# -----------------------------
# SONG RECOMMENDER
# -----------------------------

def recommend_songs(
    busy_score,
    favorite_artists,
    favorite_genres,
    top_n=10
):

    recommendations = songs.copy()

    # Convert preferences to lowercase
    favorite_artists_lower = [
        artist.lower() for artist in favorite_artists
    ]

    favorite_genres_lower = [
        genre.lower() for genre in favorite_genres
    ]


    # -----------------------------
    # FIND SONGS USER WOULD LIKE
    # -----------------------------

    recommendations["artist_match"] = (
        recommendations["artists"]
        .str.lower()
        .apply(
            lambda artists: any(
                artist.strip() in favorite_artists_lower
                for artist in artists.split(";")
            )
        )
    )

    recommendations["genre_match"] = (
        recommendations["track_genre"]
        .str.lower()
        .isin(favorite_genres_lower)
    )


    # Only consider songs matching
    # at least one user preference
    recommendations = recommendations[
        recommendations["artist_match"]
        | recommendations["genre_match"]
    ].copy()


    # -----------------------------
    # GET CALENDAR MUSIC TARGET
    # -----------------------------

    target_energy, target_valence, target_danceability = (
        get_music_targets(busy_score)
    )


    # -----------------------------
    # CALCULATE MUSIC MATCHES
    # -----------------------------

    recommendations["energy_match"] = (
        1 - abs(
            recommendations["energy"]
            - target_energy
        )
    )

    recommendations["valence_match"] = (
        1 - abs(
            recommendations["valence"]
            - target_valence
        )
    )

    recommendations["danceability_match"] = (
        1 - abs(
            recommendations["danceability"]
            - target_danceability
        )
    )


    # -----------------------------
    # PREFERENCE SCORE
    # -----------------------------

    recommendations["preference_score"] = (
        recommendations["artist_match"].astype(int) * 0.60
        +
        recommendations["genre_match"].astype(int) * 0.40
    )


    # -----------------------------
    # POPULARITY
    # -----------------------------

    recommendations["popularity_score"] = (
        recommendations["popularity"] / 100
    )


    # -----------------------------
    # FINAL SCORE
    # -----------------------------

    recommendations["score"] = (
        0.35 * recommendations["preference_score"]
        + 0.30 * recommendations["energy_match"]
        + 0.15 * recommendations["valence_match"]
        + 0.10 * recommendations["danceability_match"]
        + 0.10 * recommendations["popularity_score"]
    )


    # Highest score first
    recommendations = recommendations.sort_values(
        "score",
        ascending=False
    )


    return recommendations[
        [
            "track_name",
            "artists",
            "track_genre",
            "energy",
            "valence",
            "danceability",
            "popularity",
            "score"
        ]
    ].head(top_n)


# -----------------------------
# TEST
# -----------------------------

if __name__ == "__main__":

    # TEMPORARY:
    # your partner's calendar code will replace this
    busy_score = 80

    # TEMPORARY:
    # frontend will eventually provide these
    favorite_artists = [
        "SZA",
        "Frank Ocean",
        "Beyonce"
    ]

    favorite_genres = [
        "r-n-b",
        "pop"
    ]


    recommendations = recommend_songs(
        busy_score,
        favorite_artists,
        favorite_genres,
        top_n=10
    )


    energy, valence, danceability = (
        get_music_targets(busy_score)
    )


    print("\nBUSY SCORE:", busy_score)

    print("\nMUSIC TARGET:")
    print("Energy:", round(energy, 2))
    print("Valence:", round(valence, 2))
    print(
        "Danceability:",
        round(danceability, 2)
    )

    print("\nRECOMMENDED SONGS:\n")

    print(
        recommendations.to_string(
            index=False
        )
    )