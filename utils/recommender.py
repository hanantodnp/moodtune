import pandas as pd
import joblib
import os

# KONFIGURASI PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

# LOAD MODEL & DATA SEKALI SAJA
try:
    df = pd.read_csv(os.path.join(MODEL_DIR, "indexed_tracks.csv"))
    knn = joblib.load(os.path.join(MODEL_DIR, "knn_model.pkl"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
except FileNotFoundError:
    print("Error: Pastikan file model dan data (indexed_tracks, knn_model, scaler) ada di folder 'models/'.")
    df = pd.DataFrame() # Buat dataframe kosong agar tidak error saat import
    knn = None
    scaler = None

FEATURES = ["valence", "energy", "danceability", "tempo", "popularity_track"]

def recommend_by_song(track_id, top_n=10):
    """
    Merekomendasikan lagu berdasarkan kemiripan dengan track_id tertentu (Content-Based).
    """
    if df.empty or knn is None or scaler is None:
        return pd.DataFrame()
        
    song_data = df[df["track_id"] == track_id]

    if song_data.empty:
        return pd.DataFrame()

    song = song_data.iloc[0]
    X = scaler.transform([song[FEATURES]])
    distances, indices = knn.kneighbors(X, n_neighbors=top_n + 1)
    
    # Ambil 1..N (0 adalah lagu itu sendiri)
    recommended = df.iloc[indices[0][1:]]
    return recommended