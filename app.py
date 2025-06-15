import streamlit as st
import pickle
import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('TMDB_API_KEY')

def fetch_poster(movie_id):
    try:
        if not API_KEY:
            return "https://via.placeholder.com/500x750?text=No+API+Key"
        
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'poster_path' in data and data['poster_path']:
            return 'https://image.tmdb.org/t/p/w500' + data['poster_path']
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster"
    except Exception as e:
        st.error(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500x750?text=Error"

def recommend(movie_name):
    index = movies[movies['title'] == movie_name].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movie_list:
        # Check if movie_id exists, if not use other available ID columns
        if 'movie_id' in movies.columns:
            movie_id = movies.iloc[i[0]]['movie_id']
            recommended_movies_posters.append(fetch_poster(movie_id))
        elif 'id' in movies.columns:
            movie_id = movies.iloc[i[0]]['id']
            recommended_movies_posters.append(fetch_poster(movie_id))
        elif 'tmdb_id' in movies.columns:
            movie_id = movies.iloc[i[0]]['tmdb_id']
            recommended_movies_posters.append(fetch_poster(movie_id))
        else:
            # Use placeholder if no ID available
            recommended_movies_posters.append("https://via.placeholder.com/500x750?text=No+Poster")
        
        recommended_movies.append(movies.iloc[i[0]]['title'])
    return recommended_movies, recommended_movies_posters

movies_dict = pickle.load(open('movie_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl','rb'))

st.title('🎬 Movie Recommender System')
st.markdown("##### Find your next favorite movie 🍿")

selected_movie_name = st.selectbox(
    'Select a movie',
    movies['title'].values
)

if st.button('Show Recommendation'):
    with st.spinner('Fetching recommendations...'):
        names, poster = recommend(selected_movie_name)
        columns = st.columns(5)
        
        for i in range(5):
            with columns[i]:
                st.image(poster[i], use_container_width=True)
                st.caption(names[i])
