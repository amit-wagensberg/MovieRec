# 🎬 MovieRec

> **A data-driven movie recommendation engine based on your personal Letterboxd history and preferred categories.**

MovieRec is a web-based application built with **Streamlit (Python)** that provides smart, highly personalized movie recommendations. By parsing and analyzing official **Letterboxd** data exports (`ratings.csv` and `watched.csv`), the app extracts your historical taste profile to find patterns in what you love, and generates fresh recommendations based on your chosen movie category—strictly ensuring you are never suggested a film you have already watched.

---

## 🌟 Key Features

* **Historical Preference Extraction:** Automatically parses your Letterboxd `ratings.csv` file and extracts top-rated titles (rated 4.0 stars or higher) to accurately map your personal cinematic taste profile.
* **Strict Watchlist Guardrails:** Cross-references all potential AI outputs with your uploaded `watched.csv` file, acting as an absolute blocklist to guarantee 100% fresh, unseen recommendations.
* **Category-Based Filtering:** Allows users to pick a specific movie category or genre, combining your active selection with your historical taste profile to deliver the perfect match.
* **Locked Premium Dark Mode:** Features an aggressive custom CSS injection layout ensuring a persistent cinematic dark theme regardless of user device or local system layout preferences.
* **Real-Time Popular Feed:** Connects directly to the live TMDB API to display a curated, randomized featured title from the world's top 100 most popular movies upon loading.
* **Instant WhatsApp Sharing:** Generate customized, pre-populated WhatsApp hyperlinks to share your smart recommendations or featured picks with friends or group chats instantly.

---

## 🛠️ Tech Stack & Architecture

* **Web Framework:** [Streamlit](https://streamlit.io/) (Python framework for fast data web applications)
* **Data Engineering:** [Pandas](https://pandas.pydata.org/) (For robust local handling, parsing, and mathematical filtering of CSV datasets)
* **AI Recommendation Core:** [Google Gemini API](https://ai.google.dev/) (Leveraging advanced LLM reasoning to combine past preferences with the target category)
* **Cinematic Metadata:** [The Movie Database (TMDB) API](https://www.themoviedb.org/) (Fetches high-quality posters, backdrops, plot summaries, ratings, and trailers)

---

## 🚀 How the Application Works

1. **Dashboard Initialization:** When the application is launched, a live backend query pulls the top 100 trending global films from the TMDB directory and showcases a randomized feature selection on the landing screen.
2. **Data Ingestion:** The user uploads two official data exports extracted directly from their Letterboxd account:
   * `ratings.csv` — Processes your likes and dislikes.
   * `watched.csv` — Used exclusively as an internal exclusion list.
3. **Taste Definition Engine:** The system aggregates your top 5 highest-rated films (those marked 4.0/5.0 stars or higher).
4. **Target Selection:** The user picks a category or genre from the UI dropdown components.
5. **Context Prompt Compilation:** The engine compiles the top-rated films alongside the selected movie category and queries the Gemini model.
6. **Validation & Rendering:** The output is strictly validated against the user's `watched.csv` history. If it is a completely unseen film, the application queries TMDB for full visual media, descriptions, and trailer paths, generating a seamless dark card layout with a native WhatsApp share extension.

---

## 📦 Installation & Local Setup

### Prerequisites
Make sure you have **Python 3.8+** installed on your system.

### 1. Install Required Dependencies
Open your terminal or command prompt inside the project root folder and execute:
```bash
pip install streamlit pandas requests google-generativeai
