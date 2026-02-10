import requests
import re

API_KEY = "AIzaSyCknV0OR4dZl0Klv9C8YYSSpkwLNJC5j9c"


def get_channel_id_from_url(channel_url):
    # Case 1: /channel/UCxxxx
    match = re.search(r"/channel/(UC[a-zA-Z0-9_-]{22})", channel_url)
    if match:
        return match.group(1)

    # Case 2: @handle, /c/, /user/
    query = channel_url.rstrip("/").split("/")[-1].replace("@", "")

    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "channel",
        "maxResults": 1,
        "key": API_KEY
    }

    response = requests.get(search_url, params=params).json()

    if response.get("items"):
        return response["items"][0]["snippet"]["channelId"]

    return None


def fetch_channel_data(channel_id):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,statistics",
        "id": channel_id,
        "key": API_KEY
    }

    response = requests.get(url, params=params).json()

    if not response.get("items"):
        return None

    channel = response["items"][0]

 #STORE DATA IN VARIABLES (dictionary)
    channel_data = {
        "channel_id": channel_id,
        "channel_name": channel["snippet"]["title"],
        "description": channel["snippet"]["description"],
        "published_at": channel["snippet"]["publishedAt"],
        "subscriber_count": channel["statistics"].get("subscriberCount", None),
        "view_count": channel["statistics"].get("viewCount", 0),
        "video_count": channel["statistics"].get("videoCount", 0)
    }

    return channel_data


