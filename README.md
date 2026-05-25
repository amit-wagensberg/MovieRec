# MovieRec - https://movierec-wu5jxwnnwievum8qyhuxgb.streamlit.app/

Advanced Cinematic Intelligence Engine

MovieRec is a sophisticated recommendation system that ingests your personal **Letterboxd export data** to build a comprehensive profile of your cinematic DNA. By combining local data processing with the reasoning capabilities of the **Gemini 2.5 Flash API**, it delivers pinpoint, context-aware movie recommendations cross-referenced with deep metadata from the **TMDB API**, guaranteeing you are never recommended a film you have already watched.

---

### Core Capabilities

*   **Cinematic DNA Analysis:** Processes `ratings.csv` to extract directorial, tonal, and structural preference patterns using large language models.
*   **Strict Watch-History Filtering:** Cross-references suggestions against your 2000+ movie `watched.csv` dynamically to achieve a zero-collision recommendation rate.
*   **Group Mode Synthesis:** Merges multiple user exports to find the perfect thematic intersection for a shared viewing experience.
*   **Aggressive Dark Mode UI:** Features a custom-styled, persistent dark theme with immersive gradient cards generated via **ColorThief** dominant-color extraction.
*   **Zero-Cost Architecture:** Designed to run efficiently on Streamlit Cloud's free tier, utilizing generous API structural limits.
*   **Local Data Persistence:** Injects executed JavaScript to leverage browser `localStorage`, ensuring history and watchlists persist without a backend database.

---

### Tech Stack & Architecture

| Component | Technology | Primary Function |
| :--- | :--- | :--- |
| **Frontend Framework** | Streamlit | Reactive UI, seamless state management, and file ingestion |
| **Data Processing** | Pandas | High-performance parsing and filtering of Letterboxd CSV files |
| **Intelligence Engine** | Gemini 2.5 Flash API | Strict JSON-enforced semantic matching and taste-profile synthesis |
| **Metadata Layer** | TMDB API | Dynamic hydration of film details, provider availability, and trailer URLs |
| **Visual Processing** | ColorThief | On-the-fly image processing for atmospheric, poster-driven gradients |
| **Browser State** | streamlit_javascript | Bridging Python state logic with client-side DOM storage mechanisms |

---

### Installation & Setup

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/movierec.git
cd movierec
```

**2. Install dependencies**
```bash
pip install streamlit pandas requests colorthief streamlit-javascript
```

**3. Configure Environment Variables**
MovieRec relies on internal Streamlit secrets management to protect API keys. Create a configuration file in the `.streamlit` directory.

```bash
mkdir .streamlit
touch .streamlit/secrets.toml
```

Populate the `secrets.toml` file with your respective API keys:

```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "your_google_gemini_api_key"
TMDB_API_KEY = "your_tmdb_read_access_token_or_api_key"
```

---

### Execution

Run the Streamlit application locally:

```bash
streamlit run app.py
```

The application will launch automatically in your default internet browser. Simply export your data from Letterboxd, upload your `ratings.csv` and `watched.csv` via the sidebar, and initialize the cinematic engine.
