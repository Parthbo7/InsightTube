import re
import altair as alt
import streamlit as st
from video import get_10_recent_videos
from channel import get_channel_id_from_url, fetch_channel_data
from videodata import fetch_video_analytics
from supabase import create_client
from analytics import calculate_video_metrics, update_channel_avg_engagement
from supabase import create_client
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import matplotlib.pyplot as plt 
from supabase import create_client

st.set_page_config(layout="wide")
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


supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = create_client(supabase_url, supabase_key)

st.title("📊 Channel Analysis ")
st.divider()

channel_input = st.text_input("Enter YouTube Channel Name ")
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


with st.sidebar:
    st.markdown("## 📊 InsightTube")
    st.divider()

    st.page_link("Home.py", label="🏠 Home")
    st.page_link("pages/1_Channel_Analysis.py", label="📊 Channel Analysis")
    st.page_link("pages/2_Channel_Compare.py", label="⚔️ Channel Compare")
    st.page_link("pages/3_About_Us.py", label="🌍 About Us")


#ENTER TH YOUTUBE NAME



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
    

def parse_iso_duration(duration):
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)

    if not match:
        return 0

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    return hours * 3600 + minutes * 60 + seconds


# Display on the UI 

def run_full_channel_analysis_and_display(channel_input):
    with st.spinner("Analyzing channel... This may take a moment."):
        channel_info, video_analytics = run_full_channel_analysis(channel_input)

    if not channel_info:
        st.error("Failed to fetch channel data. Please check the URL or ID and try again.")
        return
    
    if not channel_info:
        st.error("Failed to fetch channel data.")
        return

    st.title(f"Channel Name: {channel_info['channel_name']}")
    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric("Subscribers", f"{int(channel_info['subscriber_count']):,}")
    col2.metric("Total Views", f"{int(channel_info['view_count']):,}")
    col3.metric("Total Videos", channel_info["video_count"])

    st.divider()
    st.subheader("📋 Channel Description")
    st.markdown(f"**Description:** {channel_info['description']}")
    st.divider()
    st.subheader("📅 Channel Published Date")
    st.markdown(f"**Published At:** {channel_info['published_at']}")
    st.divider()

 #Bar chart and table for video analytics views vs title  

    if video_analytics:
        df = pd.DataFrame(video_analytics)  

    st.subheader("📊 Views per Video")

    chart_df = df.sort_values(by="view_count", ascending=False)

    st.bar_chart(
        chart_df,
        x="title",
        y="view_count",
        color="#FF0000FF",
        use_container_width=True
    )
    st.divider()
    st.subheader("📊 Likes and Comments per Video")
    chart_df = pd.DataFrame({
    "Video Index": range(1, len(df) + 1),
    "Likes": df["like_count"],
    "Comments": df["comment_count"],
    })

    base = alt.Chart(chart_df).encode(
    x=alt.X("Video Index", title="Video Index")
    )

    likes_line = base.mark_line(
    color="#FF0000",
    size=3
    ).encode(
    y=alt.Y("Likes", title="Count"),
    tooltip=["Video Index", "Likes"]
    )

    comments_line = base.mark_line(
    color="#8B0000",
    size=3
    ).encode(
    y=alt.Y("Comments", title="Count"),
    tooltip=["Video Index", "Comments"]
    )

    st.altair_chart(likes_line + comments_line, use_container_width=True)




    st.divider()


    

    df = pd.DataFrame(video_analytics) if video_analytics else pd.DataFrame()

    if df.empty:
        st.warning("No video analytics data found.")
        return

    # Sort by views (better logic than just head)
    top_10_df = df.sort_values(by="view_count", ascending=False).head(10)

    average_engagement = top_10_df["engagement_per_1000"].mean()

    # Layout: Gauge on Left
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.subheader("📈 Average Engagement per 1000 Views")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=average_engagement,
            title={"text": "Engagement / 1000"},
            gauge={
                "axis": {"range": [0, 200]},
                "bar": {"color": "red"},
                "steps": [
                    {"range": [0, 50], "color": "#ffcccc"},
                    {"range": [50, 100], "color": "#ff9999"},
                    {"range": [100, 150], "color": "#ff6666"},
                    {"range": [150, 200], "color": "#cc0000"},
                ],
            }
        ))

        fig.update_layout(
            margin=dict(l=10, r=10, t=80, b=10),
            height=300,
        )

        st.plotly_chart(fig, use_container_width=True)


    with right_col:

        df = pd.DataFrame(video_analytics)

        try:
            average_views = float(df["view_count"].mean())
            total_subscribers = int(channel_info["subscriber_count"])
            subscriber_watch_percent = (
                (average_views / total_subscribers) * 100
                if total_subscribers > 0 else 0
            )
        except (ValueError, TypeError):
            subscriber_watch_percent = 0
          

        st.subheader("👥 Subscriber Watch Percentage")  
        fig_subs = go.Figure(go.Indicator(
            mode="gauge+number",
            value=subscriber_watch_percent,
            number={"suffix": "%"},
            title={"text": "Subscribers Who Watch (%)"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "red"},
                "steps": [
                    {"range": [0, 20], "color": "#ffcccc"},
                    {"range": [20, 40], "color": "#ff9999"},
                    {"range": [40, 60], "color": "#ff6666"},
                    {"range": [60, 80], "color": "#ff3333"},
                    {"range": [80, 100], "color": "#cc0000"},
                ],
            }
        ))

        fig_subs.update_layout(
            margin=dict(l=10, r=10, t=80, b=10),
            height=300,
        )

        st.plotly_chart(fig_subs, use_container_width=True)






    def categorize_duration(duration):
        total_seconds = parse_iso_duration(duration)

        if total_seconds < 120:
            return "Short (<2 min)"
        elif total_seconds <= 600:
            return "Medium (1–10 min)"
        else:
            return "Long (>10 min)"
        
   

    df["duration_category"] = df["duration"].apply(categorize_duration)

    duration_counts = df["duration_category"].value_counts().reset_index()
    duration_counts.columns = ["Category", "Count"]
    st.divider()
    #---------------------------------------------------
    # 🎥 Video Duration Distribution
    #-----------------------------------    
    left_col, right_col = st.columns([1, 1], gap="large")
    with left_col:
        
        st.subheader("🎥 Video Duration Distribution")

        red_palette = [
            "#ffcccc",   # light red
            "#ff6666",   # medium red
            "#cc0000"    # dark red
        ]

        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=duration_counts["Category"],
                    values=duration_counts["Count"],
                    hole=0.5,
                    marker=dict(
                        colors=red_palette,
                        line=dict(color="#111111", width=2)
                    ),
                    textinfo="percent+label"
                )
            ]
        )

        fig_pie.update_layout(
            height=400,
            width=400,
            margin=dict(t=30, b=10, l=10, r=10),
            showlegend=True,
            paper_bgcolor="#0e1117",   # dark background
            plot_bgcolor="#0e1117",
            font=dict(color="white")
        )

        st.plotly_chart(fig_pie, use_container_width=False)

        

    with right_col:
        # ---------------------------------------------------
        # ⏱ Duration Trend by Upload Index
        # ---------------------------------------------------
        df = df.sort_values("published_at").reset_index(drop=True)
        df["video_index"] = df.index + 1

        df["duration_minutes"] = df["duration"].apply(
            lambda x: parse_iso_duration(x) / 60 if pd.notnull(x) else 0
        )

        st.subheader("⏱ Video Duration by Upload Order")

        duration_chart = alt.Chart(df).mark_bar(
        color="#cc0000"   # Strong red
        ).encode(
        x=alt.X("video_index:O", title="Video Index"),
        y=alt.Y("duration_minutes:Q", title="Duration (Minutes)"),
        tooltip=["video_index", "duration_minutes"]
        ).properties(
            height=400
        )

        st.altair_chart(duration_chart, use_container_width=True)
                    
    # ---------------------------------------------------
    # 🔥 Upload Frequency Analysis
    # ---------------------------------------------------
    st.divider()
    st.subheader("🔥 Upload Frequency Analysis")

    try:
        total_videos = int(channel_info["video_count"])
        published_date = datetime.strptime(channel_info["published_at"][:10], "%Y-%m-%d").date()
        current_date = datetime.now().date()

        channel_age_months = (
            (current_date.year - published_date.year) * 12
            + (current_date.month - published_date.month)
        )

        if channel_age_months <= 0:
            channel_age_months = 1

        upload_frequency = total_videos / channel_age_months

    except Exception:
        channel_age_months = 1
        upload_frequency = 0

    # Classification Logic
    def classify_creator(freq):
        if freq < 1:
            return "😴 Inactive"
        elif freq < 4:
            return "🎥 Casual"
        elif freq < 8:
            return "📈 Consistent"
        else:
            return "🔥 Highly Active"

    creator_type = classify_creator(upload_frequency)

    freq_col1, freq_col2, freq_col3 = st.columns(3)

    freq_col1.metric("Channel Age (Months)", channel_age_months)
    freq_col2.metric("Uploads per Month", f"{upload_frequency:.2f}")
    freq_col3.metric("Creator Type", creator_type)

    # Gauge
    fig_freq = go.Figure(go.Indicator(
        mode="gauge+number",
        value=upload_frequency,
        title={"text": "Uploads per Month"},
        gauge={
            "axis": {"range": [0, 20]},
            "bar": {"color": "red"},
            "steps": [
                    {"range": [0, 1], "color": "#ffcccc"},
                    {"range": [1, 4], "color": "#ff9999"},
                    {"range": [4, 8], "color": "#ff6666"},
                    {"range": [8, 12], "color": "#ff3333"},
                    {"range": [12, 20], "color": "#cc0000"},
            ],
        }
    ))

    fig_freq.update_layout(
        margin=dict(l=10, r=10, t=80, b=10),
        height=300,
    )

    st.plotly_chart(fig_freq, use_container_width=True)

    


    st.divider()
    #----------------------------------------------------
    #Best Performing Video Analysis
    #---------------------------------------------------
      
    st.title("🏆 Best Performing Video Analyzer")

    df = pd.DataFrame(video_analytics)

    if df.empty:
     st.warning("Dataset is empty.")
    else:

     df["performance_score"] = (
        df["total_engagement_rate"] * 0.4 +
        df["engagement_per_1000"] * 0.3 +
        df["view_subscriber_ratio"] * 0.3
     )

     best_video = df.loc[df["performance_score"].idxmax()]

     st.subheader("🥇 Best Performing Video")

     col1, col2 = st.columns(2)

     with col1:
        st.markdown(f"""
        **Title:** {best_video['title']}  

        **Published At:** {best_video['published_at']} 

        **Views:** {best_video['view_count']}  

        **Likes:** {best_video['like_count']}  
        
        **Comments:** {best_video['comment_count']}
        """)

     with col2:
        st.metric("Engagement Rate", f"{best_video['total_engagement_rate']:.2f}%")
        st.metric("Views / Subscriber Ratio", f"{best_video['view_subscriber_ratio']:.2f}")
        st.metric("Performance Score", f"{best_video['performance_score']:.2f}")

        




    st.divider()
    st.subheader("📊 Recent Video Analytics")
    df = df.reset_index(drop=True)
    df.insert(0, "S.No", df.index + 1)

    st.dataframe(
        df,
        column_config={
            "S.No": st.column_config.NumberColumn("S.No", width="small"),
            "title": "Video Title",

            "published_at": "Published Date",

            "view_count": st.column_config.NumberColumn(
                "Views",
                format="%d 👀"
            ),

            "like_count": st.column_config.NumberColumn(
                "Likes",
                format="%d 👍"
            ),

            "comment_count": st.column_config.NumberColumn(
                "Comments",
                format="%d 💬"
            ),

            "like_ratio": st.column_config.NumberColumn(
                "Like Ratio",
                format="%.2f %%"
            ),

            "comment_ratio": st.column_config.NumberColumn(
                "Comment Ratio",
                format="%.2f %%"
            ),

            "total_engagement_rate": st.column_config.NumberColumn(
                "Engagement Rate",
                format="%.2f %%"
            ),

            "view_subscriber_ratio": st.column_config.NumberColumn(
                "View/Sub Ratio",
                format="%.2f %%"
            ),

            "engagement_per_1000": st.column_config.NumberColumn(
                "Engagement / 1000 Views",
                format="%.2f"
            ),

            "like_comment_ratio": st.column_config.NumberColumn(
                "Like-Comment Ratio",
                format="%.2f"
            ),
        },
        hide_index=True,
        use_container_width=True
        )
    
    st.divider()
      
    st.caption("© 2026 InsightTube | Built with Streamlit 💙")



if st.button("Analyze Channel"):
    if channel_input:
        run_full_channel_analysis_and_display(channel_input)
        st.toast("Channel analysis completed!", icon="✅")
    else:
        st.warning("Please enter a valid channel URL or ID.")
       
        
