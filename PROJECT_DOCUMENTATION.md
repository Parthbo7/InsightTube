# 📊 InsightTube – Comprehensive Project Documentation

## 1. Project Overview
**InsightTube** is a sophisticated YouTube Analytics Web Application built with **Streamlit**. It provides deep, actionable insights into YouTube channels and videos by leveraging the **YouTube Data API v3**, storing historical analysis in **Supabase**, and performing advanced AI-driven sentiment analysis using **Groq (Llama 3.1)**. 

The application follows a multi-page Streamlit architecture and features a premium, responsive UI with glassmorphism design elements and dynamic dark/light themes.

---

## 2. Tech Stack & Architecture
- **Frontend & Routing:** Streamlit (Multi-page setup)
- **Backend Logic:** Python 3
- **Database & Auth:** Supabase (PostgreSQL)
- **External APIs:** 
  - YouTube Data API v3 (Channels, Videos, CommentThreads)
  - Groq API (LLM for Sentiment Analysis)
- **Data Processing:** Pandas, NumPy, Scikit-learn (Linear Regression for growth prediction)
- **Data Visualization:** Plotly, Altair, Matplotlib
- **Reporting:** ReportLab (Dynamic PDF generation)

---

## 3. Directory Structure & Core Modules

### 🏠 Entry Point
- **`Home.py`**: The main landing page. It initializes the Streamlit session, injects custom CSS for styling (glassmorphism, hero sections, responsive grid), handles theme toggling (Dark/Light), and provides navigation links to the sub-pages.

### ⚙️ Core Logic & Services
- **`channel.py`**: Interacts with the YouTube API to resolve user inputs (URLs, handles, IDs) into raw Channel IDs using `get_channel_id_from_url`. Fetches basic channel statistics using `fetch_channel_data`.
- **`video.py`**: Uses the `googleapiclient` to fetch the 10 most recent video links for a given channel by parsing their "uploads" playlist.
- **`videodata.py`**: Extracts video IDs from URLs and fetches detailed metrics (views, likes, comments, duration) for a batch of videos via the YouTube API (`fetch_video_analytics`).
- **`analytics.py`**: The math engine. Calculates derived metrics for videos (e.g., `like_ratio`, `total_engagement_rate`, `engagement_per_1000`, `view_subscriber_ratio`). Also aggregates video data to update the channel's overall average engagement rate in the database.
- **`services.py`**: The orchestration layer. The `run_full_channel_analysis` function chains together channel fetching, video fetching, and analytics calculation, then securely `upserts` this data into the **Supabase** tables (`channel_info` and `video_analytics`).
- **`auth.py`**: Wraps Supabase authentication methods (`login`, `signup`).
- **`comments.py`**: Uses the YouTube `commentThreads` API to securely fetch the top 100 most relevant comments for a specific video.
- **`sentiment.py`**: The AI engine. Takes fetched comments and sends a batched prompt to the **Groq API** (`llama-3.1-8b-instant`). It is specifically prompted to understand sarcasm, Hinglish, and emojis to accurately classify comments into positive/negative/neutral, extract key themes, and provide an overall summary.
- **`components.py`**: Contains reusable UI components (like `apply_tab_styling`) to maintain consistent design across pages.

### 📄 Application Pages (`pages/` directory)
- **`1_Channel_Analysis.py`**: The most complex dashboard. 
  - Takes a channel input and triggers the full analysis pipeline.
  - Displays interactive **Plotly gauges, funnels, area charts, and bar charts**.
  - Uses **Scikit-learn (Linear Regression)** to predict subscriber growth over the next 30 days.
  - Estimates channel revenue based on average RPM formulas.
  - Features a massive **ReportLab integration** (`generate_pdf_report`) to compile all charts, tables, and AI insights into a professional, downloadable A4 PDF report.
- **`2_Channel_Compare.py`**: Benchmarks multiple creators side-by-side.
- **`3_About_Us.py`**: Information about the platform and creator.
- **`4_Trending.py`**: Discovers and analyzes currently trending YouTube content.
- **`5_Sentiment_Analysis.py`**: Dedicated UI for the Groq-powered comment sentiment analysis.

---

## 4. Data Flow & Execution Pipeline

### A. Channel Analysis Workflow
1. **Input:** User provides a channel URL or handle in `1_Channel_Analysis.py`.
2. **Resolution:** `channel.py` queries YouTube API to find the exact `channel_id`.
3. **Data Fetching:** 
   - `channel.py` gets subscriber/view counts.
   - `video.py` gets the 10 most recent video IDs.
   - `videodata.py` gets the raw stats for those 10 videos.
4. **Processing:** `analytics.py` enriches the raw stats with engagement ratios.
5. **Storage:** `services.py` upserts the enriched data into Supabase so it can be tracked historically.
6. **Visualization:** The UI renders Plotly charts (Engagement Funnel, Views Over Time, Duration vs Engagement).
7. **Prediction & Export:** A Linear Regression model predicts growth, and ReportLab can compile the current state into a PDF.

### B. Sentiment Analysis Workflow
1. **Input:** User provides a specific video URL.
2. **Extraction:** `comments.py` pulls up to 100 top comments via YouTube API.
3. **AI Processing:** `sentiment.py` formats the comments into an indexed prompt and queries the Groq API.
4. **Result:** The LLM returns a structured JSON containing sentiment indices, an overall summary, and key themes, which the UI then visualizes (likely using WordClouds and Pie charts).

---

## 5. Database Schema (Supabase)
Based on the code, the database relies on two primary tables:

### `channel_info`
- `channel_id` (Primary Key)
- `channel_name`
- `description`
- `published_at`
- `subscriber_count`
- `view_count`
- `video_count`
- `avg_engagement_rate`

### `video_analytics`
- `video_id` (Primary Key)
- `channel_id` (Foreign Key)
- `title`
- `published_at`
- `duration`
- `view_count`
- `like_count`
- `comment_count`
- `like_ratio`
- `comment_ratio`
- `total_engagement_rate`
- `view_subscriber_ratio`
- `engagement_per_1000`
- `like_comment_ratio`

---

## 6. Advanced Features & Highlights
- **AI Sentiment with Context:** The Groq prompt is custom-tailored for the Indian YouTube demographic, understanding "Hinglish", slang (e.g., "💀"), and sarcasm, making it far superior to standard NLP libraries like TextBlob.
- **Machine Learning Integration:** Uses `sklearn.linear_model.LinearRegression` based on historical upload times and view counts to project 30-day subscriber growth.
- **Enterprise Reporting:** Automatically generates high-quality PDF reports with embedded Matplotlib charts, color-coded tables, and AI insights using ReportLab.
- **Resilient API Handling:** Implements regex fallbacks for various YouTube URL formats and structured error handling for disabled comments or API quota limits.