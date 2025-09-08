# 🎬 Movie Recommender System

Welcome to the **Movie Recommender System** — a personalized, visually immersive app that suggests movies based on your taste. Built with **Streamlit**, this project blends machine learning with cinematic UI design to deliver recommendations that feel curated just for you.

---

## 🌐 Live Demo

Experience the app in action:  
👉 [Movie Recommender System — Streamlit App](https://movierecommender1980.streamlit.app/)

---

## 🚀 Features

- 🔍 Select any movie from a searchable dropdown
- 🎯 Get top 5 similar movie recommendations
- 🖼️ View stunning poster visuals with hover animations
- 🌌 Cinematic background and themed UI
- ⚙️ Powered by content-based filtering using cosine similarity

---

## 🧠 How It Works

1. **Data Source**: Uses the TMDB 5000 movies and credits dataset.
2. **Preprocessing**: Combines metadata like genres, cast, crew, and keywords.
3. **Vectorization**: Applies TF-IDF or CountVectorizer to encode movie features.
4. **Similarity Matrix**: Computes cosine similarity between movies.
5. **Recommendation Engine**: Returns top 5 most similar movies to the selected title.

---

## 🛠️ Tech Stack

- **Python**
- **Pandas**
- **Scikit-learn**
- **Streamlit**
- **Pickle** (for model serialization)
- **Git LFS** (for handling large files like `similarity.pkl`)

---

## 📦 Setup Instructions

```bash
# Clone the repo
git clone https://github.com/Sachinsingh198/MovieRecommender.git
cd MovieRecommenderSystem

# Create virtual environment
python -m venv ml_env
source ml_env/bin/activate  # or ml_env\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
