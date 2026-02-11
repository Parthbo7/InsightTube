import requests
import re

API_KEY = "AIzaSyCknV0OR4dZl0Klv9C8YYSSpkwLNJC5j9c"


def extract_video_id(url):
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"shorts/([a-zA-Z0-9_-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_video_analytics(video_links):
    if len(video_links) > 10:
        raise ValueError("Maximum 10 YouTube links allowed")

    video_ids = [extract_video_id(link) for link in video_links]
    video_ids = [vid for vid in video_ids if vid]

    if not video_ids:
        return []

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics,contentDetails",
        "id": ",".join(video_ids),
        "key": API_KEY
    }

    response = requests.get(url, params=params).json()
    analytics_data = []

    for video in response.get("items", []):
        analytics_data.append({
            "video_id": video["id"],
            "title": video["snippet"]["title"],
            "channel_name": video["snippet"]["channelTitle"],
            "published_at": video["snippet"]["publishedAt"],
            "duration": video["contentDetails"]["duration"],
            "view_count": video["statistics"].get("viewCount", 0),
            "like_count": video["statistics"].get("likeCount", 0),
            "comment_count": video["statistics"].get("commentCount", 0)
        })

    return analytics_data
