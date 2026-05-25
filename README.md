# 🎬 MovieRec (CineVibe)

> **Your Letterboxd history, curated for your current mood.**

MovieRec is an immersive, web-based movie recommendation platform built with **Streamlit (Python)**. By analyzing your personal cinematic DNA exported directly from your **Letterboxd** profile, the application delivers smart, contextual recommendations while strictly ensuring you are never suggested a film you have already watched.

---

## 🌟 Key Features

* **Letterboxd Data Ingestion:** Simple drag-and-drop file uploaders accept your `ratings.csv` and `watched.csv` exports.
* **Smart Taste Profile Analysis:** Automatically filters and aggregates your highest-rated films (rated 4.0 or higher) to recognize your specific movie taste.
* **Intelligent Guardrails (No Repeats):** Cross-references all potential recommendations against your `watched.csv` so you only get fresh recommendations.
* **Premium Immersive UI:** Features a sleek, locked **Dark Mode** design optimized for desktop and mobile displays with vibrant neon cinematic styling.
* **Live Featured Movies:** Instantly fetches the world's top 100 most popular films directly using live integration with the TMDB API.
* **Instant WhatsApp Sharing:** Share your smart recommendations or featured picks directly with friends or film groups in one click.
* **Zero-Cost Infrastructure:** Runs entirely on 100% free libraries, utilizing secure environmental configurations.

---

## 🛠️ Tech Stack & Architecture

* **Web Framework:** [Streamlit](https://streamlit.io/) (Python)
* **Data Processing:** [Pandas](https://pandas.pydata.org/) (Local CSV parsing and mathematical filtering)
* **AI Recommendation Engine:** [Google Gemini API](https://ai.google.dev/) (via the `google-generativeai` package)
* **Movie Metadata & Imagery:** [The Movie Database (TMDB) API](https://www.themoviedb.org/documentation/api) (Posters, backdrops, synopses, and ratings)

---

## 🚀 How the Application Works

1. **The Entry View:** When a user opens the web application, a beautifully styled dashboard pulls a live popular movie from TMDB's top 100 directory. 
2. **Uploading Profile Data:** The user uploads their Letterboxd data files:
   * `ratings.csv` — used to understand preferences.
   * `watched.csv` — used as an absolute filter list.
3. **Taste Definition:** The backend scripts analyze the data. Any movie given 4.0 stars or higher by the user is added to their "Favorites" list.
4. **Vibe Selection:** The user chooses a category, genre, or custom text "vibe" they are currently feeling.
5. **AI Evaluation:** The prompt compiler feeds the top 5 favorite movies and the chosen vibe into the Google Gemini model.
6. **Filtering and Rendering:** The application checks that the outputted film does not reside in `watched.csv`. If it passes, the app pulls the official movie poster, metadata, and trailer from TMDB and displays it to the user with a customized WhatsApp link.

---

## 📦 Installation & Local Setup

### Prerequisites
Make sure you have **Python 3.8+** installed on your system.

### 1. Clone or Download the Project
Ensure all script files (`app.py`, etc.) are located in your working directory.

### 2. Install Required Dependencies
Run the following command in your terminal to install the necessary libraries:
```bash
pip install streamlit pandas requests google-generativeai
