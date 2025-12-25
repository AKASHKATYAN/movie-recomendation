import pickle
import gzip
import pandas as pd
import requests
import streamlit as st
import time

# Default poster in case TMDB fails
DEFAULT_POSTER = "https://via.placeholder.com/500x750?text=No+Poster"

# -----------------------------
# Function to fetch poster safely
# -----------------------------
def fetch_poster(movie_id, retries=3, timeout=5):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return "https://image.tmdb.org/t/p/w500/" + poster_path
            else:
                return DEFAULT_POSTER
        except requests.exceptions.RequestException:
            time.sleep(1)
    return DEFAULT_POSTER

# -----------------------------
# Function to recommend movies
# -----------------------------
def recommend(movie):
    # normalize input
    movie_lower = movie.strip().lower()
    matching = movies[movies['title_lower'] == movie_lower]

    if matching.empty:
        st.warning(f"Movie '{movie}' not found in database.")
        return [], []

    index = matching.index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_names = []
    recommended_posters = []

    for i in distances[1:6]:  # top 5
        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)
        recommended_names.append(movies.iloc[i[0]].title)
        recommended_posters.append(poster)

    return recommended_names, recommended_posters

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🎬 Movie Recommender System")

# Load movies
movies_data = pickle.load(open("model/movie_dict.pkl", "rb"))
if isinstance(movies_data, dict):
    movies = pd.DataFrame(movies_data)
else:
    movies = movies_data

# Normalize titles for matching
movies['title'] = movies['title'].str.strip()
movies['title_lower'] = movies['title'].str.lower()

# Load similarity
with gzip.open("model/similarity.pkl.gz", "rb") as f:
    similarity = pickle.load(f)

# Dropdown for movie selection
selected_movie = st.selectbox("Type or select a movie from the dropdown:", movies['title'].values)

# Show recommendations
if st.button("Show Recommendation"):
    recommended_names, recommended_posters = recommend(selected_movie)

    if recommended_names:
        cols = st.columns(5)
        for col, name, poster in zip(cols, recommended_names, recommended_posters):
            col.text(name)
            col.image(poster if poster else DEFAULT_POSTER)
    else:
        st.info("No recommendations found. Please try another movie.")
