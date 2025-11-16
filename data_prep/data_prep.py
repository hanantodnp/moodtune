import os
import ast
import pandas as pd
import numpy as np


# Konfigurasi Global
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

ARTISTS_CSV = os.path.join(DATA_DIR, "artists.csv")
TRACKS_CSV = os.path.join(DATA_DIR, "tracks.csv")

OUT_CLEAN = os.path.join(DATA_DIR, "music_clean.csv")
OUT_MOOD = os.path.join(DATA_DIR, "spotify_mood_dataset.csv")

CHUNK_SIZE = 50000


# UTILITIES
def preview_columns(path):
    """Hanya membaca nama kolom tanpa load penuh."""
    return pd.read_csv(path, nrows=0).columns.tolist()


def extract_artist_from_tracks(value):
    """Mengambil nama/ID artis pertama dari kolom 'artists'."""
    try:
        if pd.isna(value):
            return np.nan
        if isinstance(value, str):
            if "['" in value or '["' in value:
                arr = ast.literal_eval(value)
                if isinstance(arr, list) and len(arr) > 0:
                    return arr[0]
            if "," in value:
                return value.split(",")[0].strip()
            return value
    except Exception:
        return value
    return value


# LOAD ARTISTS
def load_artists():
    cols = preview_columns(ARTISTS_CSV)
    want = [c for c in ["id", "name", "genres", "popularity", "followers"] if c in cols]

    artists = pd.read_csv(ARTISTS_CSV, usecols=want, low_memory=False)
    artists = artists.rename(columns={"id": "artist_id", "name": "artist_name"})
    return artists


# CLEANING TRACKS (CHUNK-BASED)
def process_chunks():
    artists = load_artists()

    # Kolom penting yang akan diekstrak dari tracks.csv
    track_cols = preview_columns(TRACKS_CSV)
    want = [
        "id", "name", "artists", "artist_id", "album_name", "release_date",
        "popularity", "duration_ms", "danceability", "energy", "loudness",
        "speechiness", "acousticness", "instrumentalness", "liveness",
        "valence", "tempo", "uri"
    ]
    want = [c for c in want if c in track_cols]

    print("Membaca kolom:", want)

    first_write = True
    total_rows = 0

    for chunk in pd.read_csv(TRACKS_CSV, usecols=want, chunksize=CHUNK_SIZE):
        
        # Normalisasi kolom
        chunk = chunk.rename(columns={"id": "track_id", "name": "track_name"})

        # Jika tidak ada artist_id, pakai parsing kolom "artists"
        if "artist_id" not in chunk.columns and "artists" in chunk.columns:
            chunk["artist_key"] = chunk["artists"].apply(extract_artist_from_tracks)
            merged = chunk.merge(
                artists, left_on="artist_key", right_on="artist_name",
                how="left", suffixes=("", "_artist")
            )
        else:
            merged = chunk.merge(artists, on="artist_id", how="left")

        # Pilih kolom penting
        keep = [
            "track_id", "track_name", "album_name", "release_date", "popularity",
            "duration_ms", "danceability", "energy", "loudness", "speechiness",
            "acousticness", "instrumentalness", "liveness", "valence", "tempo", "uri",
            "artist_name", "genres"
        ]
        keep = [c for c in keep if c in merged.columns]

        clean = merged[keep].dropna(subset=["track_name"])

        # Tulis ke file sementara
        clean.to_csv(
            OUT_CLEAN,
            mode="w" if first_write else "a",
            index=False,
            header=first_write
        )

        first_write = False
        total_rows += len(clean)
        print(f"{total_rows} baris ditulis...")

    print(f"Cleaning selesai. Total baris: {total_rows}")


# MOOD CLASSIFICATION
def classify_mood(row):
    valence = row.get("valence", np.nan)
    energy = row.get("energy", np.nan)
    dance = row.get("danceability", np.nan)
    acoustic = row.get("acousticness", np.nan)
    genres = str(row.get("genres", "")).lower()

    # Fallback
    if np.isnan(valence) or np.isnan(energy):
        if "acoustic" in genres or acoustic > 0.6:
            return "Calm"
        if any(g in genres for g in ["rock", "metal"]):
            return "Energetic"
        if "pop" in genres and dance > 0.6:
            return "Happy"
        return "Neutral"

    # Core Rules
    if valence > 0.65 and energy > 0.6:
        mood = "Happy"
    elif valence < 0.4 and energy < 0.5:
        mood = "Sad"
    elif energy > 0.7 and 0.4 <= valence <= 0.65:
        mood = "Energetic"
    elif energy < 0.5 and acoustic > 0.5:
        mood = "Calm"
    else:
        mood = "Neutral"

    # Genre Corrections
    if any(g in genres for g in ["metal", "rock", "punk"]):
        if energy > 0.6:
            mood = "Energetic"

    elif any(g in genres for g in ["jazz", "lofi", "indie", "acoustic", "ambient"]):
        if energy < 0.6:
            mood = "Calm"

    elif any(g in genres for g in ["hip hop", "rap", "trap"]):
        if valence < 0.5:
            mood = "Serious"

    elif any(g in genres for g in ["classical", "piano", "instrumental"]):
        mood = "Calm"

    elif any(g in genres for g in ["sad", "emo", "ballad"]):
        mood = "Sad"

    elif any(g in genres for g in ["pop", "dance", "disco"]):
        if valence > 0.6 and energy > 0.6:
            mood = "Happy"

    return mood



# BUILD FINAL DATASET
def build_dataset():
    print("Menggabungkan file sementara")
    df = pd.read_csv(OUT_CLEAN)

    # Hilangkan duplikat
    df = df.drop_duplicates(subset=["track_name", "artist_name"])

    # Pastikan kolom numeric ada
    for c in ["valence", "energy", "danceability", "acousticness", "tempo"]:
        if c not in df.columns:
            df[c] = np.nan

    # Tambahkan mood
    print("Mengklasifikasikan mood...")
    df["mood"] = df.apply(classify_mood, axis=1)

    # Simpan versi lengkap
    df.to_csv(OUT_MOOD, index=False)
    print("Simpan:", OUT_MOOD)

    # Simpan versi ringkas
    small_cols = [
        "track_id", "track_name", "artist_name", "genres",
        "popularity", "valence", "energy", "danceability",
        "tempo", "mood", "uri"
    ]
    small_cols = [c for c in small_cols if c in df.columns]

    df[small_cols].to_csv(os.path.join(DATA_DIR, "music_clean.csv"), index=False)
    print("Simpan: music_clean.csv")

    print("\nDataset final berhasil dibuat!")


# MAIN
if __name__ == "__main__":
    process_chunks()
    build_dataset()
