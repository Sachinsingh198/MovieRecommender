import streamlit as st
import pandas as pd
import time
import requests
import pickle

# =============== Page Config ===============
st.set_page_config(
    page_title="Movie Recommender 🎥",
    page_icon="🎬",
    layout="wide"
)

# =============== Background & Styling ===============
st.markdown(
    """
    <style>
    body {
        background-image: url("https://wallpaperaccess.com/full/329583.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .stApp {
        background-color: rgba(0, 0, 0, 0.7);
        padding: 20px;
        border-radius: 10px;
    }
    .title {
        font-size: 50px;
        font-weight: bold;
        text-align: center;
        background: -webkit-linear-gradient(45deg, #ff4b4b, #ffcc70);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 8px rgba(255,75,75,0.5);
    }
    .subtitle {
        font-size: 22px;
        text-align: center;
        color: #CFCFCF;
        margin-bottom: 30px;
    }
    .recommend-card {
        padding: 10px;
        border-radius: 15px;
        background-color: #1f1f1f;
        margin: 5px auto;
        max-width: 200px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .recommend-card:hover {
        transform: scale(1.08);
        box-shadow: 0px 6px 20px rgba(255,75,75,0.7);
    }
    .poster {
        width: 100%;
        height: 300px;
        object-fit: cover;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease-in-out;
        animation: fadeIn 1s ease-in-out;
    }
    .poster:hover {
        transform: scale(1.02);
        box-shadow: 0 0 18px rgba(255, 255, 255, 0.3);
    }
    .movie-title {
        text-align:center;
        margin-top:10px;
        font-size:16px;
        font-weight:bold;
        color:#ffffff;
    }
    .custom-selectbox label {
        font-size: 20px;
        color: #ffcc70;
        font-weight: 600;
        margin-bottom: 10px;
        display: block;
    }
    .custom-selectbox select {
        background-color: #2c2c2c;
        color: #ffffff;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #ff4b4b;
        font-size: 16px;
        width: 100%;
        box-shadow: 0 0 8px rgba(255,75,75,0.3);
    }
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =============== Sample Movie Data ===============


# Load the movie dictionary
with open("movies_dict.pkl", "rb") as f:
    movies_dict = pickle.load(f)

# Convert to DataFrame
movies = pd.DataFrame(movies_dict)

# Define poster URLs mapped to specific titles
poster_map = {
    "Parasite": "https://wallpaperbat.com/img/3000x2000/Parasite-Movie-Poster.jpg",
    "The Creator": "https://wallpaperbat.com/img/3840x2160/The-Creator-Movie-Poster.jpg",
    "The Batman": "https://wallpaperbat.com/img/5120x2880/Batman-4K-Movie-Poster.jpg",
    "Oppenheimer": "https://wallpaperbat.com/img/1920x1080/Oppenheimer-2023-Movie-Poster.jpg",
    "Borderlands": "https://wallpaperbat.com/img/3840x2160/Borderlands-Movie-Poster.jpg"
}

# Assign poster URLs based on title match
movies['poster_url'] = movies['title'].map(poster_map)
default_poster = "https://wallpaperbat.com/img/3840x2160/The-Creator-Movie-Poster.jpg"
movies['poster_url'].fillna(default_poster, inplace=True)


# Dummy similarity matrix
similarity = [
    [1, 0.8, 0.6, 0.7, 0.5],
    [0.8, 1, 0.65, 0.6, 0.55],
    [0.6, 0.65, 1, 0.75, 0.4],
    [0.7, 0.6, 0.75, 1, 0.45],
    [0.5, 0.55, 0.4, 0.45, 1]
]

# Fallback poster
DEFAULT_POSTER = "https://images.unsplash.com/photo-1517602302552-471fe67acf66?auto=format&fit=crop&w=600&q=60"

def safe_image(url: str) -> str:
    try:
        if not url:
            return DEFAULT_POSTER
        r = requests.get(url, stream=True, timeout=3)
        ct = r.headers.get("Content-Type", "")
        if r.status_code == 200 and "image" in ct.lower():
            return url
    except Exception:
        pass
    return DEFAULT_POSTER

# =============== Recommendation Logic ===============
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        ranked = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)
        ranked = [idx for idx, _ in ranked if idx != movie_index]
        top_idx = ranked[:5]
        recommended = movies.iloc[top_idx][['title', 'poster_url']]
        return recommended.reset_index(drop=True)
    except Exception:
        return pd.DataFrame({'title': [], 'poster_url': []})

def top_up_to_five(selected_title: str, rec_df: pd.DataFrame) -> list[dict]:
    cards = rec_df.to_dict('records')
    used = set([c['title'] for c in cards] + [selected_title])

    for _, row in movies.iterrows():
        if len(cards) >= 5:
            break
        if row['title'] not in used:
            cards.append({'title': row['title'], 'poster_url': row['poster_url']})
            used.add(row['title'])

    if len(cards) < 5 and selected_title not in used:
        sel_row = movies[movies['title'] == selected_title].iloc[0]
        cards.append({'title': sel_row['title'], 'poster_url': sel_row['poster_url']})
        used.add(selected_title)

    i = 0
    while len(cards) < 5 and len(cards) > 0:
        cards.append(cards[i % len(cards)])
        i += 1

    for c in cards:
        c['poster_url'] = safe_image(c.get('poster_url'))

    return cards[:5]

# =============== Header Section ===============
st.markdown('<p class="title">🎬 Movie Recommender</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Get personalized movie suggestions instantly!</p>', unsafe_allow_html=True)

# =============== Input ===============
st.markdown('<div class="custom-selectbox"><label>🍿 Choose a movie you like:</label></div>', unsafe_allow_html=True)
selected_movie_name = st.selectbox("", movies['title'].values)

if st.button("✨ Recommend Movies"):
    with st.spinner("🎥 Analyzing your taste..."):
        time.sleep(1.2)
        rec_df = recommend(selected_movie_name)
        cards = top_up_to_five(selected_movie_name, rec_df)

    st.markdown("## 🎯 Recommended For You:")

    # Tighter columns with minimal gap
    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            poster = cards[i]['poster_url']
            title = cards[i]['title']
            st.markdown(
                f"""
                <div class="recommend-card">
                    <img class="poster" src="{poster}" alt="{title} poster">
                    <div class="movie-title">👉 {title}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.success(f"✅ You selected: **{selected_movie_name}**")

# =============== Footer ===============
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; font-size:14px; color:gray;">
        Made with ❤️ using <b>Streamlit</b> <br>
        <i>Keep watching, keep smiling!</i>
    </div>
    """,
    unsafe_allow_html=True
)
