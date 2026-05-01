import requests
import streamlit as st

def fetch_top_comments(video_id, max_results=100):
    """
    Fetch top comments for a YouTube video via the commentThreads API.
    Returns (list_of_comment_dicts, error_string).
    On success, error_string is None. On failure, list is None.
    """
    try:
        API_KEY = st.secrets.get("YOUTUBE_API_KEY")
        if not API_KEY:
            raise KeyError
    except (KeyError, FileNotFoundError):
        return None, "YOUTUBE_API_KEY not found in Streamlit secrets."

    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": min(max_results, 100),
        "order": "relevance",
        "textFormat": "plainText",
        "key": API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        if response.status_code == 403:
            reason = ""
            try:
                reason = data["error"]["errors"][0]["reason"]
            except Exception:
                pass
            if reason == "commentsDisabled":
                return None, "Comments are disabled for this video."
            return None, "YouTube API access denied (403). Check your API key quota."

        if response.status_code != 200:
            msg = data.get("error", {}).get("message", f"HTTP {response.status_code}")
            return None, f"YouTube API error: {msg}"

        if "error" in data:
            return None, data["error"].get("message", "Unknown API error.")

        items = data.get("items", [])
        if not items:
            return None, "No comments found for this video."

        comments = []
        for item in items:
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            text = snippet.get("textDisplay", "").strip()
            if text:
                comments.append({
                    "text": text,
                    "author": snippet.get("authorDisplayName", ""),
                    "likes": int(snippet.get("likeCount", 0)),
                    "published_at": snippet.get("publishedAt", ""),
                })

        if not comments:
            return None, "No readable comment text found for this video."

        return comments, None

    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"
