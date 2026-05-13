import streamlit as st
import pandas as pd
import requests
import json
import os
import io
import urllib.request
import urllib.parse
import random
import base64
from colorthief import ColorThief
from streamlit_javascript import st_javascript

# ---- CONFIGURATION ----
st.set_page_config(page_title="MovieRec", page_icon="🎬", layout="wide")

# Updated minimalist styling for "Immersive UI"
st.markdown("""
    <style>
    /* Global Theme */
    .stApp {
        background-color: #0a0505;
        color: #f4f4f5;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Primary Typography */
    h1, h2, h3 {
        color: #f4f4f5 !important;
        font-weight: 700 !important;
        padding-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    /* Sidebar Separation */
    [data-testid="stSidebar"] {
        background-color: #121212;
        border-right: 1px solid #262626;
    }

    /* Primary Action Buttons */
    div.stButton > button:first-child {
        background-color: #ea580c;
        color: white;
        border-radius: 9999px;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 700;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #f97316;
        box-shadow: 0 0 15px rgba(234, 88, 12, 0.4);
        border: none;
        color: white;
    }

    /* Secondary Feedback Buttons (Outline Style) */
    div[data-testid="column"] div.stButton > button {
        background-color: transparent;
        color: #a1a1aa;
        border: 1px solid #3f3f46;
        border-radius: 8px;
        font-weight: 500;
    }
    div[data-testid="column"] div.stButton > button:hover {
        border-color: #ea580c;
        color: #ea580c;
        background-color: rgba(234, 88, 12, 0.05);
    }

    /* Clean Containers */
    [data-testid="stVerticalBlock"] > div > div[style*="border"] {
        border: 1px solid #262626 !important;
        border-radius: 12px !important;
        padding: 1.5rem;
        background-color: #0d0d0d;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        color: #ea580c !important;
        font-weight: 700;
    }

    /* Container Width */
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
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
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = 'Solo Mode'
if 'local_storage_checked' not in st.session_state:
    st.session_state.local_storage_checked = False
if 'loaded_from_mem' not in st.session_state:
    st.session_state.loaded_from_mem = False
if 'save_requested' not in st.session_state:
    st.session_state.save_requested = False
if 'clear_requested' not in st.session_state:
    st.session_state.clear_requested = False
if 'user_watchlist' not in st.session_state:
    st.session_state.user_watchlist = []
if 'user_ignore' not in st.session_state:
    st.session_state.user_ignore = []
if 'user_added_watched' not in st.session_state:
    st.session_state.user_added_watched = []
if 'active_rec' not in st.session_state:
    st.session_state.active_rec = None
if 'trigger_reroll' not in st.session_state:
    st.session_state.trigger_reroll = False

# Auto-load first:
if not st.session_state.local_storage_checked:
    val = st_javascript("localStorage.getItem('movieRecData') || 'NO_DATA'")
    if val != 0:
        if val != 'NO_DATA':
            try:
                stored = json.loads(val)
                st.session_state.ratings_data = [base64.b64decode(r) for r in stored.get('ratings', [])]
                st.session_state.watched_data = [base64.b64decode(w) for w in stored.get('watched', [])]
                st.session_state.current_mode = stored.get('mode', 'Solo Mode')
                st.session_state.user_watchlist = stored.get('watchlist', [])
                st.session_state.user_ignore = stored.get('ignore', [])
                st.session_state.user_added_watched = stored.get('added_watched', [])
                st.session_state.data_submitted = True
                st.session_state.loaded_from_mem = True
            except Exception:
                pass
        st.session_state.local_storage_checked = True
        st.rerun()

if st.session_state.save_requested:
    ratings_to_store = [base64.b64encode(r).decode('utf-8') for r in st.session_state.ratings_data] if st.session_state.ratings_data else []
    watched_to_store = [base64.b64encode(w).decode('utf-8') for w in st.session_state.watched_data] if st.session_state.watched_data else []
    data_to_store = {
        'ratings': ratings_to_store,
        'watched': watched_to_store,
        'mode': st.session_state.current_mode,
        'watchlist': st.session_state.user_watchlist,
        'ignore': st.session_state.user_ignore,
        'added_watched': st.session_state.user_added_watched
    }
    dumped = json.dumps(data_to_store)
    code = f"localStorage.setItem('movieRecData', {json.dumps(dumped)});"
    st_javascript(code)
    st.session_state.save_requested = False
    
if st.session_state.clear_requested:
    st_javascript("localStorage.removeItem('movieRecData');")
    st.session_state.clear_requested = False

# ---- SIDEBAR: FILE UPLOAD ----
with st.sidebar:
    st.header("Your Cinematic Data")
    watch_mode = st.radio("Watch Mode", ["Solo Mode", "Group Mode"], index=0 if st.session_state.current_mode == "Solo Mode" else 1)
    
    if not st.session_state.data_submitted:
        is_group = watch_mode == "Group Mode"
        if is_group:
            st.write("Upload you and your friends' Letterboxd exports to get a group recommendation.")
        else:
            st.write("Upload your Letterboxd exports to personalize recommendations.")
            
        uploaded_ratings = st.file_uploader("Upload ratings.csv", type=['csv'], accept_multiple_files=is_group)
        uploaded_watched = st.file_uploader("Upload watched.csv", type=['csv'], accept_multiple_files=is_group)
        
        if uploaded_ratings and uploaded_watched:
            if st.button("Submit Data"):
                ratings_list = uploaded_ratings if isinstance(uploaded_ratings, list) else [uploaded_ratings]
                watched_list = uploaded_watched if isinstance(uploaded_watched, list) else [uploaded_watched]
                
                valid = True
                for f in ratings_list:
                    if "rating" not in f.name.lower():
                        st.error("Invalid file. Please upload 'ratings.csv' in the first slot.")
                        valid = False
                        break
                for f in watched_list:
                    if "watched" not in f.name.lower():
                        st.error("Invalid file. Please upload 'watched.csv' in the second slot.")
                        valid = False
                        break
                
                if valid:
                    st.session_state.ratings_data = [f.getvalue() for f in ratings_list]
                    st.session_state.watched_data = [f.getvalue() for f in watched_list]
                    st.session_state.data_submitted = True
                    st.session_state.current_mode = watch_mode
                    st.session_state.loaded_from_mem = False
                    st.session_state.save_requested = True
                    st.rerun()
    else:
        if st.session_state.loaded_from_mem:
            st.success("✅ Welcome back! Your cinematic data was loaded from memory.")
            if st.button("🔴 Clear Saved Data & Restart", type="primary"):
                st.session_state.history = []
                st.session_state.user_watchlist = []
                st.session_state.user_ignore = []
                st.session_state.user_added_watched = []
                st.session_state.ratings_data = None
                st.session_state.watched_data = None
                st.session_state.data_submitted = False
                st.session_state.loaded_from_mem = False
                st.session_state.active_rec = None
                st.session_state.trigger_reroll = False
                st.session_state.local_storage_checked = False
                st.components.v1.html("""
                    <script>
                        localStorage.clear();
                        window.parent.location.reload();
                    </script>
                """, height=0)
        else:
            st.success("✅ Data loaded successfully")
            if st.button("Reset / Upload New Data"):
                st.session_state.history = []
                st.session_state.user_watchlist = []
                st.session_state.user_ignore = []
                st.session_state.user_added_watched = []
                st.session_state.ratings_data = None
                st.session_state.watched_data = None
                st.session_state.data_submitted = False
                st.session_state.active_rec = None
                st.session_state.trigger_reroll = False
                st.session_state.local_storage_checked = False
                st.components.v1.html("""
                    <script>
                        localStorage.clear();
                        window.parent.location.reload();
                    </script>
                """, height=0)

    if st.session_state.user_watchlist:
        st.markdown("---")
        st.header("Your Watchlist")
        for w_movie in reversed(st.session_state.user_watchlist):
            st.write(f"• {w_movie}")

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
ratings_df_raw_list = []
watched_df_raw_list = []

if st.session_state.data_submitted:
    try:
        r_data_iter = st.session_state.ratings_data if isinstance(st.session_state.ratings_data, list) else [st.session_state.ratings_data]
        w_data_iter = st.session_state.watched_data if isinstance(st.session_state.watched_data, list) else [st.session_state.watched_data]
        
        for r_data in r_data_iter:
            if r_data: ratings_df_raw_list.append(pd.read_csv(io.BytesIO(r_data)))
        for w_data in w_data_iter:
            if w_data: watched_df_raw_list.append(pd.read_csv(io.BytesIO(w_data)))
    except Exception as e:
        st.sidebar.error(f"Error reading loaded files: {e}")

all_top_rated_movies = []
watched_movies = []

for r_df in ratings_df_raw_list:
    if r_df is not None:
        movie_col = 'Name' if 'Name' in r_df.columns else 'Title'
        rating_col = 'Rating' if 'Rating' in r_df.columns else 'rating'
        
        if rating_col in r_df.columns:
            r_df[rating_col] = pd.to_numeric(r_df[rating_col], errors='coerce')
            high_ratings = r_df[r_df[rating_col] >= 4.0]
        else:
            high_ratings = r_df
            
        if movie_col in high_ratings.columns:
            all_top_rated_movies.extend(high_ratings[movie_col].dropna().tolist())

for w_df in watched_df_raw_list:
    if w_df is not None:
        movie_col = 'Name' if 'Name' in w_df.columns else 'Title'
        if movie_col in w_df.columns:
            watched_movies.extend(w_df[movie_col].dropna().tolist())

# Remove duplicates to save tokens
all_top_rated_movies = list(set(all_top_rated_movies))
watched_movies = list(set(watched_movies))

# ---- HELPER FUNCTIONS ----
def get_dominant_color_wrapper(image_url):
    try:
        req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            color_thief = ColorThief(io.BytesIO(response.read()))
            r, g, b = color_thief.get_color(quality=1)
            return f"{r}, {g}, {b}"
    except Exception as e:
        return "234, 88, 12" # #ea580c default

def handle_feedback(action, title, is_featured=False):
    if not st.session_state.data_submitted:
        if action == "watchlist":
            if title not in st.session_state.user_watchlist:
                st.session_state.user_watchlist.append(title)
            st.toast('Saved to your Watchlist!')
            st.session_state.save_requested = True
        elif action in ["watched", "ignore"]:
            st.session_state.featured_movie = None
        return

    if action == "watched":
        if title not in st.session_state.user_added_watched:
            st.session_state.user_added_watched.append(title)
        st.toast('Added to watched list!')
        if is_featured:
            st.session_state.featured_movie = None
        else:
            st.session_state.trigger_reroll = True
    elif action == "ignore":
        if title not in st.session_state.user_ignore:
            st.session_state.user_ignore.append(title)
        st.toast("We won't recommend this again.")
        if is_featured:
            st.session_state.featured_movie = None
        else:
            st.session_state.trigger_reroll = True
    elif action == "watchlist":
        if title not in st.session_state.user_watchlist:
            st.session_state.user_watchlist.append(title)
        st.toast('Saved to your Watchlist!')
    st.session_state.save_requested = True

def generate_recommendation(top_rated_list, watched_list, ignore_list, genre, mode="Solo Mode"):
    """Generates recommendation using Gemini 2.5 Flash via REST API."""
    all_top_rated_movies = ", ".join(top_rated_list)
    
    # Restrict string size of watched list to avoid giant prompts
    max_watched = 2000
    if len(watched_list) > max_watched:
        watched_list = watched_list[:max_watched]

    ignore_str = ", ".join(ignore_list)

    if mode == "Group Mode":
        prompt = f"""A group of friends has combined their highly rated movies (4.0 stars and above), representing their shared taste: [{all_top_rated_movies}]. Based on this combined taste profile, recommend exactly one {genre} movie. Crucially, ensure the recommendation is NOT included in this master watched list: [{watched_list}], meaning nobody in the group has seen it. 
        CRITICAL: You MUST NOT recommend any movie from this watched list: [{watched_list}], AND you MUST NOT recommend any movie from this ignored list: [{ignore_str}].
        Return ONLY the title and a short explanation of why this movie is a perfect match for their specific taste, separated by a pipe character (|). Do NOT use the word 'vibe' in your response.
        Example: Perfect Blue | Recommended because it shares the intense psychological depth, surreal visual style, and complex character studies found in your top-rated films."""
    else:
        # AGENTS.md precise prompting context
        prompt = f"""The user has highly rated the following movies (4.0 stars and above), which represent their complete cinematic taste profile: [{all_top_rated_movies}].

        Based on analyzing this entire list, recommend exactly one {genre} movie that they haven't seen yet.
        CRITICAL: You MUST NOT recommend any movie from this watched list: [{watched_list}], AND you MUST NOT recommend any movie from this ignored list: [{ignore_str}].

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
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_key}&append_to_response=videos,watch/providers,credits"
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
            
            genres = [g.get('name') for g in movie.get('genres', [])]

            cast = []
            if 'credits' in movie and 'cast' in movie['credits']:
                cast = [c.get('name') for c in movie['credits']['cast'][:5]]

            letterboxd_link = f"https://letterboxd.com/tmdb/{movie_id}"
            
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
                'id': movie_id,
                'overview': movie.get('overview', 'No synopsis available.'),
                'poster_url': poster_url,
                'year': year,
                'runtime': runtime_str,
                'rating': rating,
                'genres': genres,
                'cast': cast,
                'letterboxd_link': letterboxd_link,
                'trailer_key': trailer_key,
                'providers': providers
            }

        return None
    except Exception as e:
        st.warning(f"Could not connect to TMDB: {e}")
        return None

def fetch_featured_movie(watched_list=None, ignore_list=None):
    """Fetches a highly rated popular movie from TMDB for the empty state."""
    if watched_list is None: watched_list = []
    if ignore_list is None: ignore_list = []
    import random
    
    for _ in range(5):
        page = random.randint(1, 20)
        search_url = f"https://api.themoviedb.org/3/movie/popular?api_key={tmdb_key}&language=en-US&page={page}"
        try:
            res = requests.get(search_url)
            res.raise_for_status()
            data = res.json()
            if data.get('results'):
                movies = data['results']
                valid_movies = [m for m in movies if m.get('title') not in watched_list and m.get('title') not in ignore_list]
                
                if valid_movies:
                    basic_movie = random.choice(valid_movies)
                    movie_id = basic_movie.get('id')
                    title = basic_movie.get('title')
                    
                    # Fetch detailed movie info
                    details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_key}&append_to_response=videos,watch/providers,credits"
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
                    
                    genres = [g.get('name') for g in movie.get('genres', [])]

                    cast = []
                    if 'credits' in movie and 'cast' in movie['credits']:
                        cast = [c.get('name') for c in movie['credits']['cast'][:5]]

                    letterboxd_link = f"https://letterboxd.com/tmdb/{movie_id}"
                    
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
                        'genres': genres,
                        'cast': cast,
                        'letterboxd_link': letterboxd_link,
                        'trailer_key': trailer_key,
                        'providers': providers
                    }
        except Exception as e:
            st.warning(f"Could not connect to TMDB: {e}")
    return None

def render_featured_movie(title_text):
    combined_watched = watched_movies + st.session_state.user_added_watched if st.session_state.data_submitted else []
    ignore_list = st.session_state.user_ignore if st.session_state.data_submitted else []

    if st.session_state.featured_movie:
        feat_title = st.session_state.featured_movie.get('title')
        if st.session_state.data_submitted and (feat_title in combined_watched or feat_title in ignore_list):
            st.session_state.featured_movie = None

    if st.session_state.featured_movie is None:
        with st.spinner("Finding a featured movie..."):
            st.session_state.featured_movie = fetch_featured_movie(combined_watched, ignore_list)
            
    metadata = st.session_state.featured_movie
    if metadata:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #ea580c !important;'>{title_text}</h3>", unsafe_allow_html=True)
        with st.container(border=True):
            dom_color = get_dominant_color_wrapper(metadata['poster_url']) if metadata['poster_url'] else "234, 88, 12"
            title_html = f"<div style='background: linear-gradient(90deg, rgba({dom_color}, 0.5) 0%, transparent 100%); padding: 15px 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid rgb({dom_color});'><h2 style='margin:0; text-shadow: 1px 1px 5px rgba(0,0,0,0.5);'>{metadata['title']}</h2></div>"
            st.markdown(title_html, unsafe_allow_html=True)
            
            st.markdown(f"**📅 {metadata['year']} | ⏱️ {metadata['runtime']} min | ⭐ {metadata['rating']}/10**")
            
            if metadata.get('genres'):
                badges_html = " ".join([f"<span style='background-color: #ea580c; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; margin-right: 5px; font-weight: 500;'>{g}</span>" for g in metadata['genres']])
                st.markdown(badges_html, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

            col1, col2 = st.columns([1, 2])
            with col1:
                if metadata['poster_url']:
                    st.image(metadata['poster_url'], use_container_width=True)
                else:
                    st.write("[ Poster missing ]")
            
            with col2:
                if metadata.get('cast'):
                    st.write("### Main Cast")
                    st.write(", ".join(metadata['cast']))

                st.write("### Overview")
                st.write(metadata['overview'])

            if metadata.get('trailer_key'):
                st.write("### Trailer")
                st.video(f"https://www.youtube.com/watch?v={metadata['trailer_key']}")

            if metadata.get('providers'):
                st.write("### Where to Watch")
                st.markdown(f"**Available to stream on:** {', '.join(metadata['providers'])}")

            st.markdown("<br>", unsafe_allow_html=True)
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if metadata.get('letterboxd_link'):
                    st.markdown(f"<a href='{metadata['letterboxd_link']}' target='_blank' style='display: flex; align-items: center; justify-content: center; background-color: #1a1a1a; color: white; padding: 0.6rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; border: 1px solid #333; width: 100%; box-sizing: border-box; min-height: 45px;'>View on Letterboxd</a>", unsafe_allow_html=True)
            with action_col2:
                share_text = f"Movie Recommendation: {metadata.get('title')} ({metadata.get('year', '')})\nTMDB Rating: {metadata.get('rating', '')}/10\nGenres: {', '.join(metadata.get('genres', []))}\nView Details: {metadata.get('letterboxd_link', '')}"
                encoded_text = urllib.parse.quote(share_text)
                whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
                st.markdown(f"<a href='{whatsapp_url}' target='_blank' style='display: flex; align-items: center; justify-content: center; background-color: #25D366; color: white; padding: 0.6rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; border: none; width: 100%; box-sizing: border-box; min-height: 45px;'>Share on WhatsApp</a>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            fb_col1, fb_col2, fb_col3 = st.columns(3)
            feat_title = metadata['title']
            with fb_col1:
                st.button("Already Watched", key="feat_watch", on_click=handle_feedback, args=("watched", feat_title, True), use_container_width=True)
            with fb_col2:
                st.button("Not Interested", key="feat_ignore", on_click=handle_feedback, args=("ignore", feat_title, True), use_container_width=True)
            with fb_col3:
                st.button("Add to Watchlist", key="feat_list", on_click=handle_feedback, args=("watchlist", feat_title, True), use_container_width=True)

# ---- UI LAYOUT ----
st.title("MovieRec")

if st.session_state.data_submitted and ratings_df_raw_list and watched_df_raw_list:

    col1, col2 = st.columns(2)
    metric_label = "Group Cinematic DNA Analyzed" if st.session_state.current_mode == "Group Mode" else "High-Rated Movies Analyzed"
    watched_label = "Master Watched List Size" if st.session_state.current_mode == "Group Mode" else "Total Movies Watched"
    
    col1.metric(metric_label, len(all_top_rated_movies))
    col2.metric(watched_label, len(watched_movies))
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
    
    if rec_clicked or surprise_clicked or st.session_state.trigger_reroll:
        st.session_state.trigger_reroll = False
        st.session_state.active_rec = None
        if surprise_clicked:
            genre = random.choice(genre_list)

        if not all_top_rated_movies:
            st.warning("Insufficient data in ratings to generate accurate DNA.")
        else:
            with st.spinner("Connecting to Gemini AI..."):
                combined_watched = watched_movies + st.session_state.user_added_watched
                rec_title, rec_explanation = generate_recommendation(all_top_rated_movies, combined_watched, st.session_state.user_ignore, genre, st.session_state.current_mode)

                if rec_title:
                    with st.spinner("Fetching metadata..."):
                        metadata = fetch_tmdb_metadata(rec_title)
                        st.session_state.active_rec = {
                            'title': rec_title,
                            'explanation': rec_explanation,
                            'metadata': metadata
                        }
                        if metadata:
                            st.session_state.history.append((rec_title, metadata.get('poster_url')))

    if st.session_state.active_rec:
        show_featured = False
        rec_title = st.session_state.active_rec['title']
        rec_explanation = st.session_state.active_rec['explanation']
        metadata = st.session_state.active_rec['metadata']
        
        st.success("Analysis complete.")
        
        with st.container(border=True):
            if metadata:
                dom_color = get_dominant_color_wrapper(metadata['poster_url']) if metadata['poster_url'] else "234, 88, 12"
                title_html = f"<div style='background: linear-gradient(90deg, rgba({dom_color}, 0.5) 0%, transparent 100%); padding: 15px 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid rgb({dom_color});'><h2 style='margin:0; text-shadow: 1px 1px 5px rgba(0,0,0,0.5);'>{rec_title}</h2></div>"
                st.markdown(title_html, unsafe_allow_html=True)
                
                st.markdown(f"**📅 {metadata['year']} | ⏱️ {metadata['runtime']} min | ⭐ {metadata['rating']}/10**")
            
                if metadata.get('genres'):
                    badges_html = " ".join([f"<span style='background-color: #ea580c; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; margin-right: 5px; font-weight: 500;'>{g}</span>" for g in metadata['genres']])
                    st.markdown(badges_html, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                col1, col2 = st.columns([1, 2])
                with col1:
                    if metadata['poster_url']:
                        st.image(metadata['poster_url'], use_container_width=True)
                    else:
                        st.write("[ Poster missing ]")

                with col2:
                    st.write("### AI Match Logic")
                    st.info(rec_explanation)
                    
                    if metadata.get('cast'):
                        st.write("### Main Cast")
                        st.write(", ".join(metadata['cast']))

                    st.write("### Overview")
                    st.write(metadata['overview'])

                if metadata.get('trailer_key'):
                    st.write("### Trailer")
                    st.video(f"https://www.youtube.com/watch?v={metadata['trailer_key']}")

                if metadata.get('providers'):
                    st.write("### Where to Watch")
                    st.markdown(f"**Available to stream on:** {', '.join(metadata['providers'])}")

                action_col1, action_col2 = st.columns(2)
                with action_col1:
                    if metadata.get('letterboxd_link'):
                        st.markdown(f"<a href='{metadata['letterboxd_link']}' target='_blank' style='display: flex; align-items: center; justify-content: center; background-color: #1a1a1a; color: white; padding: 0.6rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; border: 1px solid #333; width: 100%; box-sizing: border-box; min-height: 45px;'>View on Letterboxd</a>", unsafe_allow_html=True)
                with action_col2:
                    share_text = f"Movie Recommendation: {rec_title} ({metadata.get('year', '')})\nTMDB Rating: {metadata.get('rating', '')}/10\nGenres: {', '.join(metadata.get('genres', []))}\nView Details: {metadata.get('letterboxd_link', '')}"
                    encoded_text = urllib.parse.quote(share_text)
                    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
                    st.markdown(f"<a href='{whatsapp_url}' target='_blank' style='display: flex; align-items: center; justify-content: center; background-color: #25D366; color: white; padding: 0.6rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; border: none; width: 100%; box-sizing: border-box; min-height: 45px;'>Share on WhatsApp</a>", unsafe_allow_html=True)

            else:
                st.subheader(rec_title)
                st.write("Could not fetch metadata for this title.")
                
            st.markdown("<br>", unsafe_allow_html=True)
            fb_col1, fb_col2, fb_col3 = st.columns(3)

            with fb_col1:
                st.button("Already Watched", on_click=handle_feedback, args=("watched", rec_title, False), use_container_width=True)
            with fb_col2:
                st.button("Not Interested", on_click=handle_feedback, args=("ignore", rec_title, False), use_container_width=True)
            with fb_col3:
                st.button("Add to Watchlist", on_click=handle_feedback, args=("watchlist", rec_title, False), use_container_width=True)
                            
    if show_featured:
        render_featured_movie("🎬 Featured Movie of the Day")
else:
    st.markdown("<h2 style='text-align: center; color: #ea580c !important; border-bottom: none;'>Cinematic Intelligence Engine</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a1a1aa;'>Welcome to MovieRec. Upload your Letterboxd exports (ratings.csv and watched.csv) in the sidebar and click Submit. The engine will analyze your cinematic DNA to provide highly personalized, professional recommendations tailored to your unique taste.</p>", unsafe_allow_html=True)
    render_featured_movie("🎬 Featured Movie of the Day")

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #a1a1aa;'>Powered by TMDB and Google Gemini</p>", unsafe_allow_html=True)
