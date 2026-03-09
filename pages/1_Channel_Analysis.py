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
from sklearn.linear_model import LinearRegression
import numpy as np
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

subscriber_watch_percent = 0
upload_frequency = 0
duration_counts = pd.DataFrame()

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = create_client(supabase_url, supabase_key)
st.divider()

col1, col2 = st.columns([1, 10])
col1.image("https://cdn-icons-png.flaticon.com/128/7172/7172401.png", width=80)
col2.title("Channel Analysis ")
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

def predict_subscriber_growth(df, current_subscribers):

    if df.empty:
        return current_subscribers, 0

    df = df.sort_values("published_at").reset_index(drop=True)
    df["time_index"] = df.index

    # realistic conversion
    conversion_rate = 0.005   # 0.5%

    df["estimated_sub_growth"] = df["view_count"] * conversion_rate

    X = df["time_index"].values.reshape(-1,1)
    y = df["estimated_sub_growth"].values

    model = LinearRegression()
    model.fit(X,y)

    future_index = np.array([[df["time_index"].max()+5]])

    predicted_growth = model.predict(future_index)[0]

    predicted_subscribers = current_subscribers + predicted_growth
    growth_rate = (predicted_growth/current_subscribers)*100

    return int(predicted_subscribers), growth_rate

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
    
    channel_name = channel_info["channel_name"]
    channel_id = channel_info["channel_id"]

    channel_url = f"https://www.youtube.com/channel/{channel_id}"

    st.title(f" Channel: [{channel_name}]({channel_url})")

    col1, col2, col3 = st.columns(3)

    col1.metric("Subscribers", f"{int(channel_info['subscriber_count']):,}")
    col2.metric("Total Views", f"{int(channel_info['view_count']):,}")
    col3.metric("Total Videos", channel_info["video_count"])

    st.divider()
    col1, col2 = st.columns([1,15])
    col1.image("https://cdn-icons-png.flaticon.com/128/7739/7739187.png", width=50)
    col2.subheader(" Channel Description")
    st.markdown(f"**Description:** {channel_info['description']}")
    st.divider()
    col1, col2 = st.columns([1, 15])
    col1.image("https://cdn-icons-png.flaticon.com/128/10691/10691802.png", width=50)
    col2.subheader("Channel Published Date")
    st.markdown(f"**Published At:** {channel_info['published_at']}")
    st.divider()

 #Bar chart and table for video analytics views vs title  

    if video_analytics:
        df = pd.DataFrame(video_analytics) 
    col1, col2 = st.columns([1, 15]) 
    col1.image("https://cdn-icons-png.flaticon.com/128/404/404672.png", width=50)
    col2.subheader("Views per Video")

    chart_df = df.sort_values(by="view_count", ascending=False)

    st.bar_chart(
        chart_df,
        x="title",
        y="view_count",
        color="#FF0000FF",
        use_container_width=True
    )
    st.divider()

    col1,col2 = st.columns([1,15])
    col1.image("https://cdn-icons-png.flaticon.com/128/2285/2285636.png", width=50)
    col2.subheader(" Likes and Comments per Video")
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

        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/2257/2257295.png" width="35">
            <h4 style="margin:0;">Average Engagement per 1000 Views</h4>
        </div>
        """, unsafe_allow_html=True)
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
          
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/3369/3369157.png" width="35">
            <h4 style="margin:0;">Subscriber Watch Percentage</h4>
        </div>
        """, unsafe_allow_html=True)
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
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/12670/12670512.png" width="35">
            <h4 style="margin:0;">Video Duration Distribution</h4>
        </div>
        """, unsafe_allow_html=True)

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

        
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/670/670816.png" width="35">
            <h4 style="margin:0;">Video Duration by Upload Order</h4>
        </div>
        """, unsafe_allow_html=True)


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
    st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/12822/12822821.png" width="35">
            <h4 style="margin:0;">Upload Frequency Analysis</h4>
        </div>
        """, unsafe_allow_html=True)
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
    # ---------------------------------------------------
    # 💰 Revenue Estimation Module (INR)
    # ---------------------------------------------------

    def estimate_revenue(views, cpm, monetization_rate=0.55):
        monetized_views = views * monetization_rate
        revenue = (monetized_views / 1000) * cpm
        return round(revenue, 2)

    # USD → INR
    USD_TO_INR = 90

    cpm_low_usd = 3
    cpm_high_usd = 10

    cpm_low = cpm_low_usd * USD_TO_INR
    cpm_high = cpm_high_usd * USD_TO_INR
    avg_cpm = (cpm_low + cpm_high) / 2   # ← Now ALWAYS defined


    if not df.empty and "view_count" in df.columns:

        total_recent_views = df["view_count"].sum()

        low_estimate = estimate_revenue(total_recent_views, cpm_low)
        high_estimate = estimate_revenue(total_recent_views, cpm_high)
        monthly_estimate = estimate_revenue(total_recent_views, avg_cpm)

        rpm = avg_cpm * 0.55

        # ✅ Add revenue column safely
        df["estimated_revenue"] = df["view_count"].apply(
            lambda views: estimate_revenue(views, avg_cpm)
        )

        st.divider()
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/10384/10384161.png" width="45">
            <h4 style="margin:0;"> Revenue Estimation Dashboard (INR)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)

        col1.metric("Estimated Revenue (Low)", f"₹ {low_estimate:,.2f}")
        col2.metric("Estimated Revenue (High)", f"₹ {high_estimate:,.2f}")
        col3.metric("Revenue per 1000 Views (RPM)", f"₹ {rpm:,.2f}")

    else:
        st.warning("Insufficient data to estimate revenue.")

        st.divider()

    st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/13502/13502705.png" width="45">
            <h4 style="margin:0;">Estimated Revenue per Video (INR)</h4>
        </div>
        """, unsafe_allow_html=True)
    
    # Sort by revenue
    revenue_df = df.sort_values(by="estimated_revenue", ascending=False)

    revenue_chart = alt.Chart(revenue_df).mark_bar(
        color="#cc0000"
    ).encode(
        x=alt.X("title:N", sort="-y", title="Video Title"),
        y=alt.Y("estimated_revenue:Q", title="Revenue (₹)"),
        tooltip=[
            alt.Tooltip("title", title="Video"),
            alt.Tooltip("estimated_revenue", title="Revenue (₹)", format=",.2f")
        ]
    ).properties(
        height=400
    )

    st.altair_chart(revenue_chart, use_container_width=True)
    #----------------------------------------------------
    #Best Performing Video Analysis
    #---------------------------------------------------
    st.divider()  
    st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/4302/4302106.png" width="45">
            <h4 style="margin:0;">Best Performing Recent Video Analyzer</h4>
        </div>
        """, unsafe_allow_html=True)
   
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



       
    # ---------------------------------------------------
    # 📈 Channel Growth Prediction (30 Days)
    # ---------------------------------------------------

    st.divider()

    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
    <img src="https://cdn-icons-png.flaticon.com/128/2920/2920349.png" width="40">
    <h4 style="margin:0;">Subscriber Growth Prediction (Next 30 Days)</h4>
    </div>
    """, unsafe_allow_html=True)

    current_subs = int(channel_info["subscriber_count"])

    predicted_subs, growth_rate = predict_subscriber_growth(df, current_subs)

    col1, col2, col3 = st.columns(3)

    col1.metric("Current Subscribers", f"{current_subs:,}")
    col2.metric("Predicted (30 Days)", f"{predicted_subs:,}")
    col3.metric("Growth Rate", f"{growth_rate:.2f}%")
    future = [current_subs, predicted_subs]

    growth_chart = alt.Chart(
        pd.DataFrame({
            "Stage":["Current","Predicted (30 Days)"],
            "Subscribers":future
        })
    ).mark_bar(color="#cc0000").encode(
        x="Stage",
        y="Subscribers"
    )

    st.altair_chart(growth_chart, use_container_width=True)
    # ---------------------------------------------------
    # 💡 AI-Based Channel Insights
    # ---------------------------------------------------
    st.divider()
    st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/16835/16835765.png" width="45">
            <h4 style="margin:0;">Channel Insights & Strategy Suggestions</h4>
        </div>
        """, unsafe_allow_html=True)
    insights = []

    avg_views = df["view_count"].mean()
    avg_likes = df["like_count"].mean()
    avg_comments = df["comment_count"].mean()
    avg_engagement = df["total_engagement_rate"].mean()
        # 1️⃣ Engagement Insight
    if avg_engagement > 8:
        insights.append("🔥 Excellent engagement rate. Audience is highly interactive.")
    elif avg_engagement > 4:
        insights.append("📈 Good engagement. There is room for stronger CTAs.")
    else:
        insights.append("⚠️ Low engagement. Improve thumbnails, hooks, and call-to-actions.")

    # 2️⃣ Subscriber Watch Behavior
    if subscriber_watch_percent > 40:
        insights.append("💪 Strong subscriber loyalty. Majority of subscribers actively watch.")
    elif subscriber_watch_percent > 20:
        insights.append("🤝 Moderate subscriber watching pattern.")
    else:
        insights.append("❗ Many subscribers are inactive. Focus on retention strategies.")

    # 3️⃣ Upload Consistency Insight
    if upload_frequency >= 8:
        insights.append("🔥 Highly active creator. Algorithm favors this consistency.")
    elif upload_frequency >= 4:
        insights.append("📅 Good upload consistency.")
    else:
        insights.append("😴 Upload frequency is low. Increase consistency to grow faster.")

    # 4️⃣ Duration Insight
    most_common_duration = duration_counts.iloc[0]["Category"]

    if most_common_duration == "Short (<2 min)":
        insights.append("📱 Channel focuses on short-form content. Shorts strategy detected.")
    elif most_common_duration == "Medium (1–10 min)":
        insights.append("🎬 Balanced content length. Optimized for regular YouTube videos.")
    else:
        insights.append("🎥 Long-form content dominant. Great for deep audience retention.")

    if growth_rate > 4:
        st.success("🚀 Channel is experiencing strong growth momentum.")
    elif growth_rate > 1:
        st.info("📈 Channel is showing steady growth.")
    else:
        st.warning("⚠️ Growth is currently slow.")

    # 5️⃣ Top Video Performance Gap
    top_views = df["view_count"].max()

    if top_views > avg_views * 1.8:
        insights.append("🚀 One video significantly outperformed others. Analyze and replicate its format.")
     
    # Display Insights
    for insight in insights:
        st.success(insight) 

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
    st.markdown(
        """
        <button onclick="window.print()" 
        style="
            background-color:#cc0000;
            color:white;
            padding:10px 20px;
            border:none;
            border-radius:8px;
            font-size:16px;
            cursor:pointer;">
            📄 Download Dashboard as PDF
        </button>
        """,
        unsafe_allow_html=True
    )
    


if st.button("Analyze Channel"):
    if channel_input:
        run_full_channel_analysis_and_display(channel_input)
        st.toast("Channel analysis completed!", icon="✅")
    else:
        st.warning("Please enter a valid channel URL or ID.")
        
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