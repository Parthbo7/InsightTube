import streamlit as st
import channel
from video import get_10_recent_videos  
from channel import get_channel_id_from_url, fetch_channel_data  
from videodata import API_KEY, fetch_video_analytics
from videodata import extract_video_id
from supabase import create_client

SUPABASE_URL = "https://serbtdravevbbklvqgpw.supabase.co"
SUPABASE_KEY = "sb_publishable_G9tKAh28b-498MFnvkfKXQ_LwIhPKE6"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


channel_name = input("Enter YouTube Channel Name: ")
channel_info = fetch_channel_data(get_channel_id_from_url(channel_name))

if channel_info:
    print("\n✅ Channel Info:")
    for key, value in channel_info.items():
        print(f"{key.replace('_',' ').title()}: {value}")

videos = get_10_recent_videos(channel_name)
i = 0
if videos:
    print(f"\n✅ Total videos fetched: {len(videos)}\n")
    for v in videos:
        print(f"{i}: {v}")
        i += 1
else:
    print("❌ No videos found (check channel name)")

channel_info = fetch_channel_data(get_channel_id_from_url(channel_name))
if channel_info:
    print(f"\n✅ Channel Info:")
    print(f"Name: {channel_info['channel_name']}")
    print(f"Description: {channel_info['description']}")
    print(f"Published At: {channel_info['published_at']}")
    print(f"Subscribers: {channel_info['subscriber_count']}")
    print(f"Total Views: {channel_info['view_count']}")
    print(f"Total Videos: {channel_info['video_count']}")   

video_ids = []
for link in videos:
    video_id = extract_video_id(link)
    if video_id:
        video_ids.append(video_id)
    
analytics = fetch_video_analytics(videos)

if analytics:
    print("\n📊 Video Analytics:")
    for data in analytics:
        print("--------------------------------")
        print(f"Title: {data['title']}")
        print(f"Views: {data['view_count']}")
        print(f"Likes: {data['like_count']}")
        print(f"Comments: {data['comment_count']}")
else:
    print("❌ No analytics data received")

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


analytics = fetch_video_analytics(videos)

def store_video_data(analytics_data, channel_id):

    cleaned_data = []

    for video in analytics_data:
        cleaned_data.append({
            "video_id": video["video_id"],
            "channel_id": channel_id,
            "title": video["title"],
            "published_at": video["published_at"],
            "duration": video["duration"],
            "view_count": int(video.get("view_count", 0)),
            "like_count": int(video.get("like_count", 0)),
            "comment_count": int(video.get("comment_count", 0))
        })

    response = supabase.table("video_analytics").upsert(cleaned_data).execute()

    print("\n✅ Video analytics data stored in Supabase:")


analytics = fetch_video_analytics(videos)
store_video_data(analytics, channel_info["channel_id"])

supabase.table("video_analytics").select("*").eq("channel_id", channel_info["channel_id"])

