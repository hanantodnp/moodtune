import streamlit as st
import pandas as pd
import os

# recommender.py
from recommender import Recommender
rec = Recommender()

# utils/recommender.py
from utils.recommender import recommend_by_song
from utils.ui_components import sidebar_header, header, music_card

# JUDUL HALAMAN
st.set_page_config(page_title="MoodTune", page_icon="🎧", layout="wide")

# LOAD CSS
css_path = "static/style.css"
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# SESSION
if "page" not in st.session_state:
    st.session_state.page = "Beranda"
if "selected_track_id" not in st.session_state:
    st.session_state.selected_track_id = None


# SIDEBAR
with st.sidebar:
    sidebar_header()

    menu = {
        "Beranda": "home",
        "Rekomendasi Mood": "music",
        "Temukan Lagu Serupa": "search",
        "Tentang": "about",
        "Dataset": "dataset"
    }

    for label in menu:
        if st.button(label, use_container_width=True):
            st.session_state.page = label
            # Reset selected track jika pindah halaman
            if label != "Temukan Lagu Serupa":
                st.session_state.selected_track_id = None
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

page = st.session_state.page


# HEADER
header()

# PAGES


# HOME
if page == "Beranda":
    st.header("Selamat datang di MoodTune 👋")
    st.write("Temukan lagu sesuai suasana hatimu 🎧")

    st.subheader("🎶 Rekomendasi Acak Hari Ini")
    st.write("Merekomendasikan lagu acak - KNN Model.")

    # Load data untuk sampling (dari data KNN)
    df_knn_home = pd.read_csv("models/indexed_tracks.csv")

    sample = df_knn_home.sample(6)
    for _, r in sample.iterrows():
        st.markdown(music_card(r), unsafe_allow_html=True)


# MUSIC RECOMMENDER (Sistem Ranking)
elif page == "Rekomendasi Mood":
    st.header("Pilih Mood untuk Rekomendasi Lagu")
    st.write("Merekomendasikan lagu yang paling **Populer** atau memiliki kombinasi **Valence & Energy** tertinggi untuk mood tersebut.")

    mood = st.selectbox("Pilih mood", rec.get_moods())
    jumlah = st.slider("Jumlah lagu", 5, 50, 10)
    method = st.selectbox("Metode ranking", ["popularity", "valence & energy", "random"])

    if st.button("Tampilkan 🎵"):
        with st.spinner("Mengambil lagu terbaik..."):
            # PANGGIL SISTEM RANKING
            results = rec.recommend_by_mood(mood, jumlah, method)

        for item in results:
            st.markdown(music_card(item), unsafe_allow_html=True)


# LAGU SERUPA (Sistem KNN Murni)
elif page == "Temukan Lagu Serupa":
    st.header("🎧 Temukan Lagu yang Mirip")
    st.write("Fitur ini menggunakan model **K-Nearest Neighbors** untuk menemukan 10 lagu yang memiliki fitur audio (seperti *valence* & *energy*) paling mirip dengan lagu yang Anda pilih.")

    # Load data KNN untuk pencarian
    try:
        # Load ulang untuk menghindari masalah scope
        df_knn = pd.read_csv("models/indexed_tracks.csv")
    except FileNotFoundError:
        st.error("File 'indexed_tracks.csv' tidak ditemukan di folder 'models/'.")
        st.stop()
        
    # Reset search term state jika tombol reset diklik
    if 'search_reset_flag' in st.session_state and st.session_state.search_reset_flag:
        st.session_state.song_search = ""
        st.session_state.search_reset_flag = False

    # --- Search Bar ---
    search_term = st.text_input("Ketik nama lagu atau artis...", key="song_search", placeholder="Contoh: Vigilante Man atau Ed Sheeran")

    if search_term:
        # Cari lagu berdasarkan nama (case-insensitive)
        results_df = df_knn[df_knn['track_name'].str.contains(search_term, case=False, na=False) | 
                            df_knn['artist_name'].str.contains(search_term, case=False, na=False)]

        if results_df.empty:
            st.warning(f"Tidak ada lagu yang ditemukan dengan nama/artis '{search_term}'.")
        else:
            st.subheader("Pilih lagu Anda:")
            
            # Tampilkan hasil pencarian
            for index, row in results_df.head(10).iterrows(): # Batasi 10 hasil
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.write(f"**{row['track_name']}** - *{row['artist_name']}*")
                with col2:
                    # Buat tombol untuk setiap lagu
                    if st.button(f"Pilih", key=row['track_id']):
                        st.session_state.selected_track_id = row['track_id']
                        st.session_state.search_reset_flag = False # Set flag agar tidak reset setelah pilih
                        st.rerun() # Rerun untuk menampilkan rekomendasi
                        
    # Jika ada lagu yang dipilih, tampilkan rekomendasinya
    if "selected_track_id" in st.session_state and st.session_state.selected_track_id:
        
        selected_id = st.session_state.selected_track_id
        
        # Ambil data lagu asli
        original_song = df_knn[df_knn['track_id'] == selected_id]
        if not original_song.empty:
            original_song = original_song.iloc[0]
        
            st.divider()
            st.subheader(f"Lagu Pilihan Anda:")
            st.markdown(music_card(original_song), unsafe_allow_html=True)

            st.subheader("🎶 Rekomendasi Lagu Serupa (KNN):")
            
            # PANGGIL FUNGSI KNN ANDA
            with st.spinner("Mencari lagu serupa..."):
                recommendations = recommend_by_song(selected_id, top_n=10)

            if not recommendations.empty:
                for _, r in recommendations.iterrows():
                    st.markdown(music_card(r), unsafe_allow_html=True)
            else:
                st.warning("Tidak dapat menemukan rekomendasi untuk lagu ini.")
                
            # Tombol untuk reset pencarian
            if st.button("Cari Lagu Lain"):
                st.session_state.selected_track_id = None
                st.session_state.search_reset_flag = True
                st.rerun() 
        else:
            st.session_state.selected_track_id = None # Hapus ID jika lagu tidak ditemukan
            st.rerun()


# ABOUT (Penjelasan Teknologi)
elif page == "Tentang":
    st.header("Tentang MoodTune")
    st.markdown("""
    MoodTune adalah sistem rekomendasi musik yang menggabungkan dua pendekatan utama: **Ranking Stereotip** untuk eksplorasi mood umum, dan **Content-Based Filtering** (KNN).

    ---

    ### Model yang Digunakan
    1. **Classificaton**:
        - Rekomendasi berdasarkan popularitas atau kombinasi valence & energy.
    2. **Content-Based Filtering (KNN)**:
        - Menggunakan dataset lagu yang diindeks dengan fitur audio dari Spotify.
        - Model K-Nearest Neighbors (KNN) untuk menemukan lagu serupa.
    ### Library dan Tools
    - Streamlit untuk antarmuka web interaktif.
    - Pandas dan NumPy untuk manipulasi data.
    - Scikit-learn untuk model KNN dan K-Means.
    - Spotipy untuk interaksi dengan Spotify API.
    """)

# DEBUG
elif page == "Dataset":
    st.header("Analisis Dataset")
    st.write("Bagian ini menampilkan statistik dan distribusi dataset yang digunakan dalam sistem MoodTune.")

    # Load DataFrames
    df_knn = None
    df_rank = None
    
    try:
        df_knn = pd.read_csv("models/indexed_tracks.csv")
    except FileNotFoundError:
        st.error("File 'models/indexed_tracks.csv' (Data KNN) tidak ditemukan.")

    # Ringkasan Dataset
    if df_knn is not None:
        st.subheader("Dataset (indexed_tracks.csv)")
        st.write("Dataset ini yang digunakan.")

        col_size, col_features = st.columns(2)
        with col_size:
            st.metric("Jumlah Lagu", len(df_knn))
        with col_features:
            st.metric("Jumlah Fitur", len(df_knn.columns))

        st.markdown("---")
        
        # Menampilkan Distribusi Mood
        st.subheader("Distribusi Mood (Data KNN)")

        # Distribusi mood: menggunakan bar chart
        st.bar_chart(df_knn["mood"].value_counts())

        if st.checkbox("Tampilkan Preview KNN Dataset", key='chk_knn_preview'):
            st.subheader("Preview 5 Baris Dataset KNN")
            st.dataframe(df_knn.head())
