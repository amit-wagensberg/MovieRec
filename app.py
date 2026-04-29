import streamlit as st
import pandas as pd
import requests
import json
import os
import io
import urllib.request
import random
from colorthief import ColorThief

# ---- CONFIGURATION ----
st.set_page_config(page_title="MovieRec", page_icon="🎬", layout="centered")

# Minimalist styling to match the "Immersive UI" aesthetic
st.markdown("""
    <style>
    .stApp {
        background-color: #0a0505;
        color: #f4f4f5;
    }
    h1, h2, h3 {
        color: #f4f4f5 !important;
        font-weight: 600;
        padding-bottom: 0.5rem;
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

# ---- DATA PROCESSING ----
def process_data(ratings, watched):
    if ratings is None or watched is None:
        return None, None, None
    
    # Determine column name used by Letterboxd exports ('Name' usually, fallback to 'Title')
    movie_col = 'Name' if 'Name' in ratings.columns else 'Title'
    rating_col = 'Rating' if 'Rating' in ratings.columns else 'rating'

    # Clean Data constraint: filter ratings.csv for 4.0 or higher
    if rating_col in ratings.columns:
        ratings[rating_col] = pd.to_numeric(ratings[rating_col], errors='coerce')
        high_ratings = ratings[ratings[rating_col] >= 4.0]
    else:
        high_ratings = ratings

    return high_ratings, watched, movie_col

# ---- STATE INITIALIZATION ----
if 'data_submitted' not in st.session_state:
    st.session_state.data_submitted = False
if 'ratings_data' not in st.session_state:
    st.session_state.ratings_data = None
if 'watched_data' not in st.session_state:
    st.session_state.watched_data = None
if 'featured_movie' not in st.session_state:
    st.session_state.featured_movie = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'surprise_trigger' not in st.session_state:
    st.session_state.surprise_trigger = False
if 'surprise_genre' not in st.session_state:
    st.session_state.surprise_genre = 'Action'

# ---- SIDEBAR: FILE UPLOAD ----
with st.sidebar:
    st.header("Your Cinematic Data")
    if not st.session_state.data_submitted:
        st.write("Upload your Letterboxd exports to personalize recommendations.")
        uploaded_ratings = st.file_uploader("Upload ratings.csv", type=['csv'])
        uploaded_watched = st.file_uploader("Upload watched.csv", type=['csv'])
        
        if uploaded_ratings is not None and uploaded_watched is not None:
            if st.button("Submit Data"):
                r_name = uploaded_ratings.name.lower()
                w_name = uploaded_watched.name.lower()
                
                if "rating" not in r_name:
                    st.error("Invalid file. Please upload 'ratings.csv' in the first slot.")
                elif "watched" not in w_name:
                    st.error("Invalid file. Please upload 'watched.csv' in the second slot.")
                else:
                    st.session_state.ratings_data = uploaded_ratings.getvalue()
                    st.session_state.watched_data = uploaded_watched.getvalue()
                    st.session_state.data_submitted = True
                    st.rerun()
    else:
        st.success("✅ Data loaded successfully")
        if st.button("Reset / Upload New Data"):
            st.session_state.data_submitted = False
            st.session_state.ratings_data = None
            st.session_state.watched_data = None
            st.rerun()

    if st.session_state.history:
        st.markdown("---")
        st.header("Session History")
        for h_title, h_poster in reversed(st.session_state.history):
            h_col1, h_col2 = st.columns([1, 3])
            with h_col1:
                if h_poster:
                    st.image(h_poster, use_container_width=True)
            with h_col2:
                st.write(f"**{h_title}**")

# Load data based on uploads
import io
ratings_df_raw, watched_df_raw = None, None

if st.session_state.data_submitted:
    try:
        ratings_df_raw = pd.read_csv(io.BytesIO(st.session_state.ratings_data))
        watched_df_raw = pd.read_csv(io.BytesIO(st.session_state.watched_data))
    except Exception as e:
        st.sidebar.error(f"Error reading loaded files: {e}")

ratings_df, watched_df, movie_col = process_data(ratings_df_raw, watched_df_raw)

# ---- HELPER FUNCTIONS ----
def get_user_taste(ratings, col_name):
    if ratings is None or col_name not in ratings.columns:
        return []
    # Take all highly rated movies to define cinematic DNA
    return ratings[col_name].dropna().tolist()

def get_watched_list(watched, col_name):
    if watched is None or col_name not in watched.columns:
        return []
    return watched[col_name].dropna().tolist()

def get_dominant_color_wrapper(image_url):
    try:
        req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            color_thief = ColorThief(io.BytesIO(response.read()))
            r, g, b = color_thief.get_color(quality=1)
            return f"{r}, {g}, {b}"
    except Exception as e:
        return "234, 88, 12" # #ea580c default

def generate_recommendation(top_rated_list, watched_list, genre):
    """Generates recommendation using Gemini 2.5 Flash via REST API."""
    all_top_rated_movies = ", ".join(top_rated_list)
    
    # Restrict string size of watched list to avoid giant prompts
    max_watched = 2000
    if len(watched_list) > max_watched:
        watched_list = watched_list[:max_watched]

    # AGENTS.md precise prompting context
    prompt = f"""The user has highly rated the following movies (4.0 stars and above), which represent their complete cinematic taste profile: [{all_top_rated_movies}].

    Based on analyzing this entire list, recommend exactly one {genre} movie that they haven't seen yet.
    Crucially, ensure the recommendation is NOT included in their watched history here: [{watched_list}].

    Return ONLY the title and a short, professional explanation of why this movie is a perfect match for their specific taste, separated by a pipe character (|). Do NOT use the word 'vibe' in your response.
    Example: Perfect Blue | Recommended because it shares the intense psychological depth, surreal visual style, and complex character studies found in your top-rated films."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key.strip()}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Explicit error message extraction to inform the user about key expiry
        if response.status_code == 400:
            err_data = response.json()
            err_msg = err_data.get("error", {}).get("message", "Unknown Bad Request")
            st.error(f"Gemini API Error (400 Bad Request): {err_msg}")
            return None, None
            
        response.raise_for_status()
        data = response.json()

        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()

        # Parse title and explanation based on pipe delimiter
        if "|" in text:
            parts = text.split("|", 1)
            return parts[0].strip(), parts[1].strip()
        else:
            # Fallback if AI didn't follow formatting strictly
            return text.replace("Title:", "").replace("*", "").strip(), "A professional cinematic recommendation tailored to your taste."

    except Exception as e:
        st.error(f"Failed to generate recommendation via Gemini API: {e}")
        return None, None

def fetch_tmdb_metadata(movie_title):
    """Fetches comprehensive metadata from TMDB."""
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_key}&query={movie_title}"
    try:
        res = requests.get(search_url)
        res.raise_for_status()
        data = res.json()

        if data.get('results'):
            basic_movie = data['results'][0]
            movie_id = basic_movie.get('id')
            
            # Fetch detailed movie info
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_key}&append_to_response=videos,watch/providers"
            det_res = requests.get(details_url)
            det_res.raise_for_status()
            movie = det_res.json()
            
            poster_path = movie.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            
            release_date = movie.get('release_date', '')
            year = release_date.split('-')[0] if release_date else 'Unknown'
            runtime = movie.get('runtime')
            runtime_str = str(runtime) if runtime else 'Unknown'
            rating = round(movie.get('vote_average', 0), 1)
            
            trailer_key = None
            if 'videos' in movie and 'results' in movie['videos']:
                for video in movie['videos']['results']:
                    if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                        trailer_key = video.get('key')
                        break
            
            providers = []
            if 'watch/providers' in movie and 'results' in movie['watch/providers']:
                us_providers = movie['watch/providers']['results'].get('US', {})
                if 'flatrate' in us_providers:
                    providers = [p.get('provider_name') for p in us_providers['flatrate']]
            
            return {
                'overview': movie.get('overview', 'No synopsis available.'),
                'poster_url': poster_url,
                'year': year,
                'runtime': runtime_str,
                'rating': rating,
                'trailer_key': trailer_key,
                'providers': providers
            }

        return None
    except Exception as e:
        st.warning(f"Could not connect to TMDB: {e}")
        return None

def fetch_featured_movie():
    """Fetches a highly rated popular movie from TMDB for the empty state."""
    import random
    search_url = f"https://api.themoviedb.org/3/movie/popular?api_key={tmdb_key}&language=en-US&page=1"
    try:
        res = requests.get(search_url)
        res.raise_for_status()
        data = res.json()
        if data.get('results'):
            movies = data['results']
            basic_movie = random.choice(movies[:10])
            movie_id = basic_movie.get('id')
            title = basic_movie.get('title')
            
            # Fetch detailed movie info
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_key}&append_to_response=videos,watch/providers"
            det_res = requests.get(details_url)
            det_res.raise_for_status()
            movie = det_res.json()
            
            poster_path = movie.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            
            release_date = movie.get('release_date', '')
            year = release_date.split('-')[0] if release_date else 'Unknown'
            runtime = movie.get('runtime')
            runtime_str = str(runtime) if runtime else 'Unknown'
            rating = round(movie.get('vote_average', 0), 1)
            
            trailer_key = None
            if 'videos' in movie and 'results' in movie['videos']:
                for video in movie['videos']['results']:
                    if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                        trailer_key = video.get('key')
                        break
            
            providers = []
            if 'watch/providers' in movie and 'results' in movie['watch/providers']:
                us_providers = movie['watch/providers']['results'].get('US', {})
                if 'flatrate' in us_providers:
                    providers = [p.get('provider_name') for p in us_providers['flatrate']]
            
            return {
                'title': title,
                'overview': movie.get('overview', 'No synopsis available.'),
                'poster_url': poster_url,
                'year': year,
                'runtime': runtime_str,
                'rating': rating,
                'trailer_key': trailer_key,
                'providers': providers
            }
    except Exception as e:
        st.warning(f"Could not connect to TMDB: {e}")
    return None

def render_featured_movie(title_text):
    if st.session_state.featured_movie is None:
        with st.spinner("Finding a featured movie..."):
            st.session_state.featured_movie = fetch_featured_movie()
            
    metadata = st.session_state.featured_movie
    if metadata:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #ea580c !important;'>{title_text}</h3>", unsafe_allow_html=True)
        with st.container(border=True):
            dom_color = get_dominant_color_wrapper(metadata['poster_url']) if metadata['poster_url'] else "234, 88, 12"
            title_html = f"<div style='background: linear-gradient(90deg, rgba({dom_color}, 0.5) 0%, transparent 100%); padding: 15px 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid rgb({dom_color});'><h2 style='margin:0; text-shadow: 1px 1px 5px rgba(0,0,0,0.5);'>{metadata['title']}</h2></div>"
            st.markdown(title_html, unsafe_allow_html=True)
            
            st.markdown(f"**📅 {metadata['year']} | ⏱️ {metadata['runtime']} min | ⭐ {metadata['rating']}/10**")
            col1, col2 = st.columns([1, 2])
            with col1:
                if metadata['poster_url']:
                    st.image(metadata['poster_url'], use_container_width=True)
                else:
                    st.write("[ Poster missing ]")
            
            with col2:
                st.write("### Overview")
                st.write(metadata['overview'])

            if metadata['trailer_key']:
                st.write("### Trailer")
                st.video(f"https://www.youtube.com/watch?v={metadata['trailer_key']}")

            if metadata['providers']:
                st.write("### Where to Watch")
                st.markdown(f"**Available to stream on:** {', '.join(metadata['providers'])}")

# ---- UI LAYOUT ----
st.title("MovieRec")

if st.session_state.data_submitted and ratings_df is not None and watched_df is not None:
    all_top_rated_movies = get_user_taste(ratings_df, movie_col)
    watched_movies = get_watched_list(watched_df, movie_col)

    col1, col2 = st.columns(2)
    col1.metric("High-Rated Movies Analyzed", len(all_top_rated_movies))
    col2.metric("Total Movies Watched", len(watched_movies))
    st.markdown("---")

    # Inputs
    genre_list = ['Action', 'Comedy', 'Drama', 'Sci-Fi', 'Horror', 'Thriller', 'Romance', 'Documentary', 'Mystery', 'Fantasy']
    genre = st.selectbox("What genre do you want to watch today?", genre_list)

    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        rec_clicked = st.button("Analyze & Recommend")
    with btn_col2:
        surprise_clicked = st.button("🎲 Surprise Me!")

    show_featured = True
    if rec_clicked or surprise_clicked:
        if surprise_clicked:
            genre = random.choice(genre_list)

        if not all_top_rated_movies:
            st.warning("Insufficient data in ratings to generate accurate DNA.")
        else:
            with st.spinner("Connecting to Gemini AI..."):
                rec_title, rec_explanation = generate_recommendation(all_top_rated_movies, watched_movies, genre)

                if rec_title:
                    show_featured = False
                    st.success("Analysis complete.")
                    
                    with st.container(border=True):
                        with st.spinner("Fetching metadata..."):
                            metadata = fetch_tmdb_metadata(rec_title)

                            if metadata:
                                dom_color = get_dominant_color_wrapper(metadata['poster_url']) if metadata['poster_url'] else "234, 88, 12"
                                title_html = f"<div style='background: linear-gradient(90deg, rgba({dom_color}, 0.5) 0%, transparent 100%); padding: 15px 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid rgb({dom_color});'><h2 style='margin:0; text-shadow: 1px 1px 5px rgba(0,0,0,0.5);'>{rec_title}</h2></div>"
                                st.markdown(title_html, unsafe_allow_html=True)
                                
                                st.markdown(f"**📅 {metadata['year']} | ⏱️ {metadata['runtime']} min | ⭐ {metadata['rating']}/10**")
                            
                                col1, col2 = st.columns([1, 2])
                                with col1:
                                    if metadata['poster_url']:
                                        st.image(metadata['poster_url'], use_container_width=True)
                                    else:
                                        st.write("[ Poster missing ]")

                                with col2:
                                    st.write("### AI Match Logic")
                                    st.info(rec_explanation)
                                    
                                    st.write("### Overview")
                                    st.write(metadata['overview'])

                                if metadata['trailer_key']:
                                    st.write("### Trailer")
                                    st.video(f"https://www.youtube.com/watch?v={metadata['trailer_key']}")

                                if metadata['providers']:
                                    st.write("### Where to Watch")
                                    st.markdown(f"**Available to stream on:** {', '.join(metadata['providers'])}")

                                st.session_state.history.append((rec_title, metadata.get('poster_url')))
                            else:
                                st.subheader(rec_title)
                                st.write("Could not fetch metadata for this title.")
                            
    if show_featured:
        render_featured_movie("🎬 Featured Random Movie (Not Personalized)")
else:
    st.markdown("<h2 style='text-align: center; color: #ea580c !important; border-bottom: none;'>Cinematic Intelligence Engine</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a1a1aa;'>Welcome to MovieRec. Upload your Letterboxd exports (ratings.csv and watched.csv) in the sidebar and click Submit. The engine will analyze your cinematic DNA to provide highly personalized, professional recommendations tailored to your unique taste.</p>", unsafe_allow_html=True)
    render_featured_movie("🎬 Featured Movie of the Day")

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #a1a1aa;'>Powered by TMDB and Google Gemini</p>", unsafe_allow_html=True)
