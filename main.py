from video import get_10_recent_videos
from channel import get_channel_id_from_url, fetch_channel_data
from videodata import fetch_video_analytics
from supabase import create_client
from analytics import calculate_video_metrics, update_channel_avg_engagement

# =========================
# SUPABASE CONFIG
# =========================

SUPABASE_URL = "https://serbtdravevbbklvqgpw.supabase.co"
SUPABASE_KEY = ""

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# USER INPUT
# =========================

channel_input = input("Enter YouTube Channel URL or Name: ")

# =========================
# FETCH CHANNEL DATA
# =========================

channel_id = get_channel_id_from_url(channel_input)
channel_info = fetch_channel_data(channel_id)

if not channel_info:
    print("❌ Channel not found")
    exit()


# =========================
# FETCH CHANNEL DATA FROM DB
# =========================

channel_db = (
    supabase
    .table("channel_info")
    .select("*")
    .eq("channel_id", channel_id)
    .execute()
)

print("\n📺 Channel Data From Database:")

for row in channel_db.data:
    print("--------------------------------------------------")
    print(f"Channel Name: {row['channel_name']}")
    print(f"Subscribers: {row['subscriber_count']}")
    print(f"Total Views: {row['view_count']}")
    print(f"Total Videos: {row['video_count']}")
    print(f"Published At: {row['published_at']}")
    
    # Optional metrics if columns exist
    if row.get("avg_engagement_rate") is not None:
        print(f"Avg Engagement: {round(row['avg_engagement_rate'], 2)}%")

    if row.get("upload_frequency") is not None:
        print(f"Upload Frequency: {round(row['upload_frequency'], 2)} videos/month")
# =========================
# STORE CHANNEL DATA
# =========================

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

print("\n✅ Channel data stored successfully")

# =========================
# FETCH RECENT VIDEOS
# =========================

videos = get_10_recent_videos(channel_input)

if not videos:
    print("❌ No videos found")
    exit()

print(f"\n✅ {len(videos)} Videos Fetched")

# =========================
# FETCH VIDEO ANALYTICS
# =========================

analytics = fetch_video_analytics(videos)

if not analytics:
    print("❌ No analytics data received")
    exit()

# =========================
# STORE VIDEO ANALYTICS
# =========================

subscriber_count = int(channel_info["subscriber_count"])

cleaned_data = []

for video in analytics:   # ✅ fixed here

    video_id = video["video_id"]
    view_count = int(video.get("view_count", 0))
    like_count = int(video.get("like_count", 0))
    comment_count = int(video.get("comment_count", 0))

    # 🔥 Call external function
    metrics = calculate_video_metrics(video, subscriber_count)

    cleaned_data.append({
        "video_id": video_id,
        "channel_id": channel_id,
        "title": video["title"],
        "published_at": video["published_at"],
        "duration": video["duration"],
        "view_count": view_count,
        "like_count": like_count,
        "comment_count": comment_count,

        # calculated values
        "like_ratio": metrics["like_ratio"],
        "comment_ratio": metrics["comment_ratio"],
        "total_engagement_rate": metrics["total_engagement_rate"],
        "view_subscriber_ratio": metrics["view_subscriber_ratio"],
        "engagement_per_1000": metrics["engagement_per_1000"],
        "like_comment_ratio": metrics["like_comment_ratio"]
    })

# ✅ Actually store in Supabase 

supabase.table("video_analytics").upsert(cleaned_data).execute()

print("✅ Video analytics stored successfully")

update_channel_avg_engagement(supabase, channel_id)



# =========================
# FETCH LATEST CHANNEL DATA
# =========================

channel_db = (
    supabase
    .table("channel_info")
    .select("*")
    .eq("channel_id", channel_id)
    .execute()
)

print("\n================ CHANNEL SUMMARY ================")

for row in channel_db.data:
    print(f"Channel Name: {row['channel_name']}")
    print(f"Subscribers: {row['subscriber_count']}")
    print(f"Total Views: {row['view_count']}")
    print(f"Total Videos: {row['video_count']}")
    print(f"Published At: {row['published_at']}")

    if row.get("avg_engagement_rate") is not None:
        print(f"Avg Engagement: {round(row['avg_engagement_rate'], 2)}%")
# =========================
# FETCH STORED DATA FROM DB
# =========================

stored_data = (
    supabase
    .table("video_analytics")
    .select("*")
    .eq("channel_id", channel_info["channel_id"])
    .execute()
)

print("\n📦 Stored Data From Database:")
for row in stored_data.data:
    print("--------------------------------------------------")
    print(f"Title: {row['title']}")
    print(f"Views: {row['view_count']}")
    print(f"Likes: {row['like_count']}")
    print(f"Comments: {row['comment_count']}")
    print(f"Like Ratio: {round(row['like_ratio'], 2)}%")
    print(f"Comment Ratio: {round(row['comment_ratio'], 2)}%")
    print(f"Engagement Rate: {round(row['total_engagement_rate'], 2)}%")
    print(f"View/Sub Ratio: {round(row['view_subscriber_ratio'], 2)}%")
    print(f"Engagement per 1000: {round(row['engagement_per_1000'], 2)}")
    print(f"Like/Comment Ratio: {round(row['like_comment_ratio'], 2)}")
    print()

