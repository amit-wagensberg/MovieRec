# 🎬 MovieRec: Cinematic Intelligence Engine

MovieRec is a premium, AI-powered movie recommendation dashboard built with Streamlit. By analyzing your highly-rated films from Letterboxd, it builds your unique "Cinematic DNA" and uses Google's Gemini AI to recommend exactly what you should watch next—ensuring it's a movie you haven't seen before.

## ✨ Features

* **🧠 AI-Powered Recommendations:** Utilizes **Google Gemini 2.5 Flash** to analyze your taste and provide highly personalized movie suggestions with a logical explanation of *why* it fits your profile.
* **📊 Letterboxd Integration:** Seamlessly processes your `ratings.csv` and `watched.csv` Letterboxd exports to understand your preferences (filters for movies rated 4.0 and above) and prevent duplicate recommendations.
* **🎥 Rich TMDB Metadata:** Fetches comprehensive movie details via the **TMDB API**, including:
  * Official Posters & Synopses
  * Release Year, Runtime, and TMDB Rating
  * **Embedded YouTube Trailers**
  * **Where to Watch:** Live streaming providers availability (Netflix, Apple TV, Amazon, etc.)
* **🎨 Dynamic Premium UI:** Uses `ColorThief` to extract the dominant color from the movie's poster and dynamically generates a sleek, glowing gradient background for the movie title.
* **🎲 Surprise Me! Roulette:** Can't pick a genre? Let the engine randomly select one for you and generate an instant recommendation.
* **📜 Session History:** A dedicated sidebar keeping track of all the recommendations you received during your current session.

## 🛠️ Technologies Used

* **Frontend/Backend:** [Streamlit](https://streamlit.io/) (Python)
* **Data Handling:** Pandas
* **AI Model:** Google Gemini API (`gemini-2.5-flash`)
* **Movie Data:** TMDB API
* **UI Styling:** Custom CSS, HTML, and `ColorThief`

## 🚀 Getting Started

### Prerequisites
1. Python 3.9+
2. A Google Gemini API Key ([Get it here](https://aistudio.google.com/))
3. A TMDB API Key ([Get it here](https://developer.themoviedb.org/docs/getting-started))
4. Your Letterboxd Data (Export your data from Letterboxd settings to get `ratings.csv` and `watched.csv`).

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/MovieRec.git](https://github.com/yourusername/MovieRec.git)
   cd MovieRec
