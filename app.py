import pickle
import streamlit as st
import requests
import gzip
import pandas as pd

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if poster_path:
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    else:
        return None  # return None if no poster

def recommend(movie):
    # check if movie exists
    matching = movies[movies['title'] == movie]
    if matching.empty:
        st.warning(f"Movie '{movie}' not found in database.")
        return [], []

    index = matching.index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)
        recommended_movie_posters.append(poster)
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

st.header('Movie Recommender System')

# load movies
movies_data = pickle.load(open('model/movie_dict.pkl','rb'))
# ensure movies is a DataFrame
if isinstance(movies_data, dict):
    movies = pd.DataFrame(movies_data)
else:
    movies = movies_data

# load compressed similarity
with gzip.open('model/similarity.pkl.gz', 'rb') as f:
    similarity = pickle.load(f)

# strip extra spaces in titles
movies['title'] = movies['title'].str.strip()

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    if recommended_movie_names:
        cols = st.columns(5)  # use new st.columns
        for col, name, poster in zip(cols, recommended_movie_names, recommended_movie_posters):
            col.text(name)
            if poster:
                col.image(poster)
            else:
                col.text("No poster available")
