import streamlit as st
from streamlit_lottie import st_lottie
from services import load_lottieurl
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
    col1.image("https://cdn-icons-png.flaticon.com/128/2593/2593453.png", width=40)
    col2.page_link("pages/5_Sentiment_Analysis.py", label="Sentiment Analysis")
    col1,col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/934/934478.png", width=40)
    col2.page_link("pages/2_Channel_Compare.py", label="Channel Compare")
    col1,col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/9227/9227001.png", width=40)
    col2.page_link("pages/4_Trending.py", label="Trending Videos")
    col1,col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/9985/9985768.png", width=40)
    col2.page_link("pages/3_About_Us.py", label=" About Us")

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
.block-container { padding-top: 2rem; }
[data-testid="stSidebar"] { background-color: #111827; }
.stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; }

/* ── Hero ── */
.hero-header {
    font-size: 3rem !important;
    font-weight: 800;
    margin-bottom: 5px;
    background: linear-gradient(135deg, #F8FAFC 0%, #94A3B8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-subtitle {
    color: #94A3B8;
    font-size: 1.1rem;
    margin-bottom: 25px;
}

/* ── Video Card ── */
.video-card {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 15px;
    transition: all 0.3s ease;
    margin-bottom: 15px;
    height: 100%;
}
.video-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(239, 68, 68, 0.15);
    border-color: rgba(239, 68, 68, 0.3);
}
</style>
""", unsafe_allow_html=True)

from components import apply_tab_styling
apply_tab_styling()

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
# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; margin-top: 20px; animation: fadeIn 0.8s ease-out;">
    <img src="https://cdn-icons-png.flaticon.com/128/9227/9227001.png" width="80" style="margin-bottom: 10px;">
    <h1 class="hero-header">Trending Videos</h1>
    <p class="hero-subtitle">Discover what's trending across YouTube categories in real-time</p>
</div>
""", unsafe_allow_html=True)


# -------------------------
# INPUT SECTION
# -------------------------

col_in1, col_in2, col_in3 = st.columns([1, 6, 1])
with col_in2:
    category_name = st.selectbox(
        "📂 Select Category",
        list(categories.keys())
    )
    category_id = categories[category_name]
    
    st.markdown("""
    <p style="color: #64748B; font-size: 0.9rem; margin-top: -10px; margin-bottom: 20px; text-align: center;">
        <i>Trending: Music, Gaming, News</i>
    </p>
    """, unsafe_allow_html=True)
    
    analyze_btn = st.button("🚀 Analyze Trends", use_container_width=True, type="primary")

if not analyze_btn:
    st.markdown("""
    <div style="text-align: center; margin-top: 60px; padding: 40px; border: 2px dashed #334155; border-radius: 20px; opacity: 0.6; animation: fadeIn 1s ease-out;">
        <img src="https://cdn-icons-png.flaticon.com/128/9227/9227001.png" width="60" style="filter: grayscale(100%); opacity: 0.5;">
        <h3 style="color: #64748B; margin-top: 15px;">Select a category to explore trending videos</h3>
        <p style="color: #475569;">Real-time YouTube analytics and top charts will appear here.</p>
    </div>
    """, unsafe_allow_html=True)
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
if analyze_btn:

    lottie_trend = load_lottieurl("https://lottie.host/149f706a-a289-48c0-8f69-7b3b3558c736/U6Y6Y6p1p.json")
    
    with st.spinner("Fetching latest trends..."):
        if lottie_trend:
            st_lottie(lottie_trend, height=200, key="trend_lottie")
        df = get_trending_videos(category_id)

    if df is None or df.empty:
        st.error("No trending videos found for this category.")
        st.stop()

    tab1, tab2, tab3, tab4 = st.tabs(["🔥 Top Videos", "🏆 Top Channels", "📊 Analytics", "🧠 Insights"])

    with tab1:
        st.subheader("📺 Top Trending Videos")
        st.divider()

        cols_per_row = 3
        for i in range(0, len(df), cols_per_row):
            cols = st.columns(cols_per_row)
            for col, (_, row) in zip(cols, df.iloc[i:i+cols_per_row].iterrows()):
                with col:
                    channel_icon = get_channel_icon(row["channel_id"])
                    video_url = f"https://www.youtube.com/watch?v={row['video_id']}"
                    title_trunc = row['title'][:50] + "..." if len(row['title']) > 50 else row['title']
                    st.markdown(f"""
                    <a href="{video_url}" target="_blank" style="text-decoration: none; color: inherit;">
                        <div class="video-card">
                            <img src="{row['thumbnail']}" style="width: 100%; border-radius: 8px; margin-bottom: 10px;">
                            <div style="font-weight: 600; font-size: 1rem; margin-bottom: 8px; color: #f1f5f9; line-height: 1.3;">{title_trunc}</div>
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                                <img src="{channel_icon}" style="width: 24px; height: 24px; border-radius: 50%;">
                                <span style="font-size: 0.9rem; color: #94a3b8;">{row['channel']}</span>
                            </div>
                            <div style="font-size: 0.8rem; color: #64748b; display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px;">
                                <span>👁 {row['views']:,} views</span>
                                <span>👍 {row['likes']:,} likes</span>
                            </div>
                        </div>
                    </a>
                    """, unsafe_allow_html=True)

    with tab2:
        st.subheader("🏆 Leading Channels in this Category")
        st.divider()

        top_channels = df.groupby(["channel","channel_id"]).agg({
            "views":"sum",
            "title":"count"
        }).reset_index()

        top_channels = top_channels.rename(columns={"title":"trending_videos"})
        top_channels = top_channels.sort_values(by="views", ascending=False).head(12).reset_index(drop=True)

        channel_ids = top_channels["channel_id"].tolist()
        icons = get_channel_icons(channel_ids)

        for i in range(0, len(top_channels), cols_per_row):
            cols = st.columns(cols_per_row)
            for col, (_, row) in zip(cols, top_channels.iloc[i:i+cols_per_row].iterrows()):
                with col:
                    rank = top_channels.index.get_loc(row.name) + 1
                    icon = icons.get(row["channel"], None)
                    st.markdown(f"### #{rank}")
                    if icon:
                        st.image(icon, width=70)
                    st.markdown(f"**{row['channel']}**")
                    st.caption(f"🔥 {row['trending_videos']} Trending Videos")
                    st.caption(f"👁 {row['views']:,} Views")
                    channel_url = f"https://youtube.com/channel/{row['channel_id']}"
                    st.link_button("Visit Channel", channel_url, use_container_width=True)
                    st.divider()

    with tab3:
        st.subheader("📊 Category Analytics")
        st.divider()
        
        c1, c2 = st.columns(2)
        with c1:
            chart = px.pie(df, values="views", names="channel", title="Views Share by Channel", hole=0.4)
            chart.update_layout(template="plotly_dark")
            st.plotly_chart(chart, use_container_width=True)
        
        with c2:
            engage_chart = px.bar(df.sort_values("engagement", ascending=False).head(10),
                                  x="engagement", y="title", orientation="h", title="Top Engagement Leaderboard",
                                  color_discrete_sequence=["#ef4444"])
            engage_chart.update_layout(template="plotly_dark", yaxis={'showticklabels':False})
            st.plotly_chart(engage_chart, use_container_width=True)

        st.divider()
        st.subheader("📋 Trending Data Grid")
        st.data_editor(
            df[["title", "channel", "views", "likes", "comments", "engagement"]],
            column_config={
                "title": "Video Title",
                "channel": "Channel",
                "views": st.column_config.NumberColumn("Views", format="%d"),
                "likes": st.column_config.NumberColumn("Likes", format="%d"),
                "comments": st.column_config.NumberColumn("Comments", format="%d"),
                "engagement": st.column_config.NumberColumn("Engagement", format="%d"),
            },
            hide_index=True,
            use_container_width=True,
            disabled=True
        )

    with tab4:
        st.subheader("🧠 Intelligence Insights")
        avg_views = df["views"].mean()
        
        if avg_views > 5_000_000:
            st.success("🔥 This category is highly competitive. Mass appeal content is currently dominating.")
        elif avg_views > 1_000_000:
            st.info("📈 Good growth category. Steady audience engagement detected.")
        else:
            st.warning("⚠️ Lower viral traction. Niche content might be better here.")
            
        st.divider()
        st.markdown("### 💡 Strategy Suggestion")
        most_active_channel = df['channel'].value_counts().idxmax()
        st.info(f"**{most_active_channel}** is the most active channel in this trending list. Analyzing their recent uploads could provide valuable content hooks.")
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