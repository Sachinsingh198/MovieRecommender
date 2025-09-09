import streamlit as st
import pandas as pd
import pickle
import time
import requests

# ================== Page Config ==================
st.set_page_config(
    page_title="Movie Recommender 🎥",
    page_icon="🎬",
    layout="wide"
)

# ================== Background & Styling ==================
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
        padding: 15px;
        border-radius: 20px;
        background-color: #1f1f1f;
        margin: 10px auto;
        max-width: 280px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.6);
        transition: transform 0.4s ease, box-shadow 0.4s ease;
    }
    .recommend-card:hover {
        transform: scale(1.12);
        box-shadow: 0px 8px 25px rgba(255,75,75,0.8);
    }
    .poster {
        width: 100%;
        height: 360px;
        object-fit: cover;
        border-radius: 15px;
        animation: fadeIn 1s ease-in-out;
    }
    .movie-title {
        text-align:center;
        margin-top:12px;
        font-size:18px;
        font-weight:bold;
        color:#ffffff;
    }
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================== Load Data ==================
with open("movies_dict.pkl", "rb") as f:
    movies_dict = pickle.load(f)
movies = pd.DataFrame(movies_dict)

with open("similarity.pkl", "rb") as f:
    similarity = pickle.load(f)

# Fallback poster
DEFAULT_POSTER = "https://images.unsplash.com/photo-1517602302552-471fe67acf66?auto=format&fit=crop&w=600&q=60"

# ================== Helper Functions ==================
def safe_image(url: str) -> str:
    """Return a working image URL, fallback if broken."""
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

def recommend(movie):
    """Return top 5 similar movies."""
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
    """Ensure 5 unique recommendations (no duplicates)."""
    cards = rec_df.to_dict('records')
    used = set([c['title'] for c in cards] + [selected_title])

    # Fill with unique movies until we have 5
    if len(cards) < 5:
        extra = movies[~movies['title'].isin(used)].sample(
            n=min(5-len(cards), len(movies)-len(used)), replace=False
        )
        for _, row in extra.iterrows():
            cards.append({'title': row['title'], 'poster_url': row.get('poster_url', DEFAULT_POSTER)})
            used.add(row['title'])

    # Ensure posters are valid
    for c in cards:
        c['poster_url'] = safe_image(c.get('poster_url'))

    return cards[:5]

# ================== Header ==================
st.markdown('<p class="title">🎬 Movie Recommender</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Get personalized movie suggestions instantly!</p>', unsafe_allow_html=True)

# ================== Input ==================
selected_movie_name = st.selectbox(
    "🍿 Choose a movie you like:",
    movies['title'].values
)

if st.button("✨ Recommend Movies"):
    with st.spinner("🎥 Analyzing your taste..."):
        time.sleep(1.2)
        rec_df = recommend(selected_movie_name)
        cards = top_up_to_five(selected_movie_name, rec_df)

    st.markdown("## 🎯 Recommended For You:")
    cols = st.columns([1.4, 1.4, 1.4, 1.4, 1.4], gap="large")

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

# ================== Footer ==================
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
