import streamlit as st

def sidebar_header():
    with st.container():
        left_co, cent_co,last_co = st.columns(3)
        with cent_co:
            st.image("assets/teslogo.png", width=60,)
        
        st.markdown("""
            <h2 style="color:#06b6d4; margin-bottom:0; text-align:center;">MoodTune</h2>
            <p style="color:gray; font-size:0.9em; text-align:center;">Smart Music Recommender</p>
            <hr style="margin:0.5rem 0; border-color:#334155;">
        """, unsafe_allow_html=True)


def header():
    st.markdown("""
    <div class="header">
        <div class="logo-title">
            <span class="title">MoodTune</span>
        </div>
        <p class="subtitle">🎧 Rekomendasi Musik Pintar Berdasarkan Mood — Spotify Dataset Kaggle</p>
    </div>
    """, unsafe_allow_html=True)


def music_card(track):
    track_id = track.get("track_id") or track.get("id") or ""
    return f"""
    <div class="music-card">
        <h4 style="margin-bottom:4px;">🎵 {track.get('track_name')}</h4>
        <p style="color:#cbd5e1;margin-top:0;">
            {track.get('artist_name')} |
            Valence: {track.get('valence')} |
            Energy: {track.get('energy')} |
            Popularity: {track.get('popularity_track')}
        </p>
        {'<iframe style="border-radius:12px;margin-top:10px;" src="https://open.spotify.com/embed/track/'+track_id+'" width="100%" height="84"></iframe>' if track_id else ''}
    </div>
    """
