import streamlit as st
import pandas as pd
import google.generativeai as genai
import requests
import os

# ---- CONFIGURATION ----
st.set_page_config(page_title="CineVibe", page_icon="🎬", layout="centered")

# Minimalist styling to match the "Immersive UI" vibe
st.markdown("""
    <style>
    .stApp {
        background-color: #0a0505;
        color: #f4f4f5;
    }
    h1, h2, h3 {
        color: #ea580c !important;
        text-transform: uppercase;
        font-style: italic;
    }
    .stButton > button {
        background-color: #ea580c;
        color: white;
        border-radius: 9999px;
        border: none;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #c2410c;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ---- SECRETS MANAGEMENT ----
def get_secrets():
    # Helper to gracefully check for secrets
    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
        tmdb_key = st.secrets["TMDB_API_KEY"]
        return gemini_key, tmdb_key
    except FileNotFoundError:
        st.error("Secrets file not found. Please create `.streamlit/secrets.toml` locally, or add them to Streamlit Cloud's secrets panel.")
        st.stop()
    except KeyError as e:
        st.error(f"Missing API Key: {e}. Please add it to your secrets.")
        st.stop()

gemini_key, tmdb_key = get_secrets()
genai.configure(api_key=gemini_key)

# ---- DATA PROCESSING ----
@st.cache_data
def load_and_filter_data():
    try:
        ratings = pd.read_csv("data/ratings.csv")
        watched = pd.read_csv("data/watched.csv")
        
        # Determine column name used by Letterboxd exports ('Name' usually, fallback to 'Title')
        movie_col = 'Name' if 'Name' in ratings.columns else 'Title'
        rating_col = 'Rating' if 'Rating' in ratings.columns else 'rating'
        
        # Clean Data constraint: filter ratings.csv for 4.0 or higher
        if rating_col in ratings.columns:
            high_ratings = ratings[ratings[rating_col] >= 4.0]
        else:
            high_ratings = ratings
            
        return high_ratings, watched, movie_col
    except FileNotFoundError as e:
        st.warning(f"File not found: {e.filename}. Please add standard Letterboxd 'ratings.csv' and 'watched.csv' to the 'data/' folder.")
        return None, None, None

ratings_df, watched_df, movie_col = load_and_filter_data()

# ---- HELPER FUNCTIONS ----
def get_user_taste(ratings, col_name, limit=5):
    if ratings is None or col_name not in ratings.columns:
        return []
    # Take the top N movies to define cinematic DNA
    return ratings[col_name].head(limit).tolist()

def get_watched_list(watched, col_name):
    if watched is None or col_name not in watched.columns:
        return []
    return watched[col_name].tolist()

def generate_recommendation(top_5, watched_list, mood):
    """Generates recommendation using Gemini 1.5 Flash."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    top_5_str = ", ".join(top_5)
    
    # AGENTS.md precise prompting context
    prompt = f"The user loves {top_5_str}. Recommend one {mood} movie they haven't seen (not in {watched_list}). Return ONLY the title and a 1-sentence 'vibe' explanation separated by a pipe character (|). Example: Perfect Blue | A neon-soaked psychological descent into the blurred lines of identity and fame."
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Parse title and vibe based on pipe delimiter
        if "|" in text:
            parts = text.split("|", 1)
            return parts[0].strip(), parts[1].strip()
        else:
            # Fallback if AI didn't follow formatting strictly
            return text.replace("Title:", "").replace("*", "").strip(), "A cinematic journey tailored to your DNA."
            
    except Exception as e:
        st.error(f"Failed to generate recommendation with Gemini: {e}")
        return None, None

def fetch_tmdb_metadata(movie_title):
    """Fetches posters and overviews from TMDB."""
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_key}&query={movie_title}"
    try:
        res = requests.get(search_url)
        res.raise_for_status()
        data = res.json()
        
        if data.get('results'):
            movie = data['results'][0]
            poster_path = movie.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            return movie.get('overview'), poster_url
            
        return "No synopsis available.", None
    except Exception as e:
        st.warning(f"Could not connect to TMDB: {e}")
        return None, None

# ---- UI LAYOUT ----
st.title("CineVibe")

if ratings_df is not None and watched_df is not None:
    top_5_movies = get_user_taste(ratings_df, movie_col)
    watched_movies = get_watched_list(watched_df, movie_col)
    
    st.write("### Taste Foundations")
    st.write("Synthesizing cinematic DNA from your top-rated films:")
    if top_5_movies:
        st.code(", ".join(top_5_movies))
    else:
        st.write("*Requires rated movies.*")
    
    # Inputs
    mood = st.selectbox("What's the current mood?", ["Melancholy", "Adrenaline", "Comfort", "Slow Burn", "Analog Horror", "Neo-Noir"])
    
    if st.button("Analyze & Recommend"):
        if not top_5_movies:
            st.warning("Insufficient data in ratings to generate accurate DNA.")
        else:
            with st.spinner("Connecting to Gemini AI..."):
                rec_title, rec_vibe = generate_recommendation(top_5_movies, watched_movies, mood)
                
                if rec_title:
                    # Divider for output
                    st.markdown("---")
                    
                    st.subheader(rec_title)
                    st.markdown(f"**Vibe:** *{rec_vibe}*")
                    
                    with st.spinner("Fetching metadata..."):
                        synopsis, poster = fetch_tmdb_metadata(rec_title)
                        
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            if poster:
                                st.image(poster, use_container_width=True)
                            else:
                                st.write("[ Poster missing ]")
                                
                        with col2:
                            st.write("### Overview")
                            st.write(synopsis)
                        
                        st.success("Analysis complete.")
else:
    st.info("Awaiting Data Context. Please populate the `data/` folder.")
