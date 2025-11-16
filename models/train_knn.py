import os
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import joblib

# PATH CONFIG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

INPUT_PATH = os.path.join(DATA_DIR, "music_clean.csv")
MODEL_PATH = os.path.join(BASE_DIR, "knn_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
INDEXED_PATH = os.path.join(BASE_DIR, "indexed_tracks.csv")

# FITUR YANG ADA DI DATA KAMU
FEATURES = ["valence", "energy", "danceability", "tempo", "popularity"]

def train_knn():
    print("Loading dataset")
    df = pd.read_csv(INPUT_PATH)

    # Pastikan semua fitur tersedia
    available = [c for c in FEATURES if c in df.columns]
    print("Fitur dipakai:", available)

    df = df.dropna(subset=available)
    print("Jumlah baris setelah dropna:", len(df))

    # Ekstrak fitur numeric
    X = df[available]

    # Scaling fitur
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Simpan scaler
    joblib.dump(scaler, SCALER_PATH)
    print("Scaler saved:", SCALER_PATH)

    # Train KNN
    knn = NearestNeighbors(n_neighbors=10, metric="euclidean")
    knn.fit(X_scaled)

    # Simpan model
    joblib.dump(knn, MODEL_PATH)
    print("Model KNN saved:", MODEL_PATH)

    # Simpan indexed tracks
    index_df = df[[
        "track_id",
        "track_name",
        "artist_name",
        "genres",
        "mood"
    ] + available]

    index_df.to_csv(INDEXED_PATH, index=False)
    print("indexed_tracks.csv saved:", INDEXED_PATH)

    print("\nTRAINING SELESAI TANPA ERROR!\n")

if __name__ == "__main__":
    train_knn()
