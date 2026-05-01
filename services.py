from video import get_10_recent_videos
from channel import get_channel_id_from_url, fetch_channel_data
from videodata import fetch_video_analytics
from supabase import create_client
from analytics import calculate_video_metrics, update_channel_avg_engagement
import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()  # loads .env file

try:
    import streamlit as st
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Failed to initialize Supabase client: {e}")
    supabase = None


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def run_full_channel_analysis(channel_input):

    channel_id = get_channel_id_from_url(channel_input)
    channel_info = fetch_channel_data(channel_id)

    if not channel_info:
        return None, None

    # Store channel
    channel_data = {
        "channel_id": channel_info["channel_id"],
        "channel_name": channel_info["channel_name"],
        "description": channel_info["description"],
        "published_at": channel_info["published_at"],
        "subscriber_count": int(channel_info["subscriber_count"]),
        "view_count": int(channel_info["view_count"]),
        "video_count": int(channel_info["video_count"])
    }

    supabase.table("channel_info").upsert(channel_data).execute()

    # Fetch videos
    videos = get_10_recent_videos(channel_input)
    analytics = fetch_video_analytics(videos)

    subscriber_count = int(channel_info["subscriber_count"])
    cleaned_data = []

    for video in analytics:
        metrics = calculate_video_metrics(video, subscriber_count)

        cleaned_data.append({
            "video_id": video["video_id"],
            "channel_id": channel_id,
            "title": video["title"],
            "published_at": video["published_at"],
            "duration": video["duration"],
            "view_count": int(video.get("view_count", 0)),
            "like_count": int(video.get("like_count", 0)),
            "comment_count": int(video.get("comment_count", 0)),
            "like_ratio": metrics["like_ratio"],
            "comment_ratio": metrics["comment_ratio"],
            "total_engagement_rate": metrics["total_engagement_rate"],
            "view_subscriber_ratio": metrics["view_subscriber_ratio"],
            "engagement_per_1000": metrics["engagement_per_1000"],
            "like_comment_ratio": metrics["like_comment_ratio"]
        })

    supabase.table("video_analytics").upsert(cleaned_data).execute()

    update_channel_avg_engagement(supabase, channel_id)

    # Fetch stored final data
    stored_data = (
        supabase
        .table("video_analytics")
        .select("*")
        .eq("channel_id", channel_id)
        .execute()
    )

    return channel_info, stored_data.data
