import streamlit as st
import pandas as pd
import plotly.express as px
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
        <img src="https://cdn-icons-png.flaticon.com/512/1384/1384060.png" width="40">
        <h3 style="margin:0;">InsightTube</h3>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/10307/10307931.png", width=40)
    col2.page_link("Home.py", label="Home")
    col1,col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/404/404672.png", width=40)
    col2.page_link("pages/1_Channel_Analysis.py", label="Channel Analysis")
    col1,col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/934/934478.png", width=40)
    col2.page_link("pages/2_Channel_Compare.py", label="Channel Compare")
    col1,col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/9227/9227001.png", width=40)
    col2.page_link("pages/4_Trending.py", label="Trending Videos")
    col1,col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/9985/9985768.png", width=40)
    col2.page_link("pages/3_About_Us.py", label=" About Us")
    col1,col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/2593/2593453.png", width=40)
    col2.page_link("pages/5_Sentiment_Analysis.py", label="Sentiment Analysis")

st.set_page_config(
    page_title="InsightTube",
    layout="wide",
    initial_sidebar_state="expanded"
)

hide_default_sidebar = """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(hide_default_sidebar, unsafe_allow_html=True)   
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
[data-testid="stSidebar"] {
    background-color: #111827;
}
.stMetric {
    background-color: #1f2937;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

def get_channel_icons(channel_ids):

    request = youtube.channels().list(
        part="snippet",
        id=",".join(channel_ids)
    )

    response = request.execute()

    icons = {}

    for item in response["items"]:
        icons[item["snippet"]["title"]] = item["snippet"]["thumbnails"]["default"]["url"]

    return icons
# -------------------------
# YOUTUBE API SETUP
# -------------------------

try:
    API_KEY = st.secrets["YOUTUBE_API_KEY"]
except:
    import os
    API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

# -------------------------
# ALL YOUTUBE CATEGORIES
# -------------------------

categories = {
    "All": None,
    "Film & Animation": "1",
    "Autos & Vehicles": "2",
    "Music": "10",
    "Pets & Animals": "15",
    "Sports": "17",
    "Gaming": "20",
    "Videoblogging": "21",
    "People & Blogs": "22",
    "Comedy": "23",
    "Entertainment": "24",
    "News & Politics": "25",
    "How to & Style": "26",
    "Science & Technology": "28",
    
}
st.divider()
col1,col2 = st.columns([1,10])
col1.image("https://cdn-icons-png.flaticon.com/128/9227/9227001.png", width=80)
col2.title("Trending Videos")
st.divider()


# -------------------------
# CATEGORY SELECT
# -------------------------

category_name = st.selectbox(
    "Select Category",
    list(categories.keys())
)

category_id = categories[category_name]
def get_channel_icon(channel_id):

    request = youtube.channels().list(
        part="snippet",
        id=channel_id
    )

    response = request.execute()

    return response["items"][0]["snippet"]["thumbnails"]["default"]["url"]
# -------------------------
# FETCH TRENDING VIDEOS
# -------------------------

def get_trending_videos(category_id=None):

    try:

        params = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": "IN",
            "maxResults": 25
        }

        if category_id:
            params["videoCategoryId"] = category_id

        request = youtube.videos().list(**params)

        response = request.execute()

    except HttpError:
        return None

    videos = []

    for item in response["items"]:

        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        channel_id = item["snippet"]["channelId"]

        views = int(item["statistics"].get("viewCount", 0))
        likes = int(item["statistics"].get("likeCount", 0))
        comments = int(item["statistics"].get("commentCount", 0))

        thumbnail = item["snippet"]["thumbnails"]["medium"]["url"]

        engagement = likes + comments

        videos.append({
            "title": title,
            "channel": channel,
            "channel_id": channel_id,
            "views": views,
            "likes": likes,
            "comments": comments,
            "engagement": engagement,
            "thumbnail": thumbnail,
            "video_id": item["id"]
        })

    return pd.DataFrame(videos)


# -------------------------
# RUN ANALYSIS
# -------------------------
if st.button("Analyze Trends"):

    df = get_trending_videos(category_id)

    if df is None:
        st.error("No trending videos found for this category.")
        st.stop()

    st.subheader("📺 Top Trending Videos")
    st.divider()

    cols_per_row = 3   # number of cards per row

    for i in range(0, len(df), cols_per_row):

        cols = st.columns(cols_per_row)

        for col, (_, row) in zip(cols, df.iloc[i:i+cols_per_row].iterrows()):

            with col:

                channel_icon = get_channel_icon(row["channel_id"])

                st.image(row["thumbnail"], use_container_width=True)

                st.markdown(f"**{row['title']}**")

                icon_col, name_col = st.columns([1,4])

                with icon_col:
                    st.image(channel_icon, width=30)

                with name_col:
                    st.write(row["channel"])

                st.caption(f"👁 {row['views']:,} views")
                st.caption(f"👍 {row['likes']:,} likes")
                st.caption(f"💬 {row['comments']:,} comments")

                video_url = f"https://www.youtube.com/watch?v={row['video_id']}"
                st.link_button("▶ Watch", video_url, use_container_width=True)
    # -------------------------
    # TOP CHANNELS
    # -------------------------
    
    st.title("🏆 Top Channels")
    st.divider()

    top_channels = df.groupby(["channel","channel_id"]).agg({
        "views":"sum",
        "title":"count"
    }).reset_index()

    top_channels = top_channels.rename(columns={
        "title":"trending_videos"
    })

    top_channels = top_channels.sort_values(
        by="views",
        ascending=False
    ).head(12).reset_index(drop=True)


    # fetch icons
    channel_ids = top_channels["channel_id"].tolist()
    icons = get_channel_icons(channel_ids)


    cols_per_row = 3

    for i in range(0, len(top_channels), cols_per_row):

        cols = st.columns(cols_per_row)

        for col, (_, row) in zip(cols, top_channels.iloc[i:i+cols_per_row].iterrows()):

            with col:

                rank = top_channels.index.get_loc(row.name) + 1

                icon = icons.get(row["channel"], None)

                if icon:
                    st.image(icon, width=70)

                st.markdown(f"### #{rank} {row['channel']}")

                st.caption(f"🔥 {row['trending_videos']} Trending Videos")
                st.caption(f"👁 {row['views']:,} Views")

                channel_url = f"https://youtube.com/channel/{row['channel_id']}"
                st.link_button("Visit Channel", channel_url, use_container_width=True)

                st.divider()
            

    # -------------------------
    # PIE CHART
    # -------------------------

    st.title("📊 Views Distribution")

    chart = px.pie(
        df,
        values="views",
        names="channel",
        title="Views Share by Channel"
    )

    st.plotly_chart(chart, use_container_width=True)

    # -------------------------
    # ENGAGEMENT CHART
    # -------------------------
    st.divider()
    st.title("📈 Engagement Leaderboard")

    engage_chart = px.bar(
        df.sort_values("engagement", ascending=False).head(10),
        x="engagement",
        y="title",
        orientation="h"
    )

    st.plotly_chart(engage_chart, use_container_width=True)

    # -------------------------
    # AI INSIGHT
    # -------------------------
    st.divider()
    st.title("🧠 Trend Insight")

    avg_views = df["views"].mean()

    if avg_views > 5_000_000:
        st.success(
            "This category is highly competitive with massive view counts. "
            "Only high-quality or viral content performs well."
        )

    elif avg_views > 1_000_000:
        st.info(
            "This category has good engagement and steady growth potential."
        )

    else:
        st.warning(
            "This category currently has lower viral traction."
        )
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #0E1117;
    color: white;
    text-align: right;
    padding: 10px;
    font-size: 14px;
}
</style>

<div class="footer">
    © 2026 InsightTube | Built with Streamlit 💙 | Pbo7
</div>
""", unsafe_allow_html=True)