import altair as alt

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase_auth import datetime
from services import run_full_channel_analysis


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

st.divider()
col1,col2 = st.columns([1,10])
col1.image("https://cdn-icons-png.flaticon.com/128/934/934478.png", width=80)
col2.title("Channel Comparison")
st.divider()

col1, col2 = st.columns(2,gap="large")

with col1:
    channel_1_input = st.text_input("Enter First Channel Name or URL")

with col2:
    channel_2_input = st.text_input("Enter Second Channel Name or URL")




# Run analysis when button clicked
compare_btn = st.button("Compare Channels 🚀")

if compare_btn:

    if channel_1_input and channel_2_input:

        with st.spinner("Analyzing channels... ⏳", show_time=True):

            info1, data1 = run_full_channel_analysis(channel_1_input)
            info2, data2 = run_full_channel_analysis(channel_2_input)

            if info1 and info2:
                st.session_state["info1"] = info1
                st.session_state["data1"] = data1
                st.session_state["info2"] = info2
                st.session_state["data2"] = data2

                st.toast("Channel analysis completed! ✅")

            else:
                st.error("Failed to analyze one or both channels.")

    else:
        st.warning("Please enter both channel URLs or IDs.")

if "info1" in st.session_state and "info2" in st.session_state:

    info1 = st.session_state["info1"]
    info2 = st.session_state["info2"]
    data1 = st.session_state["data1"]
    data2 = st.session_state["data2"]

    col1, col2, = st.columns(2,gap="large")

    with col1:
        st.subheader(f"📌 {info1['channel_name']}")
        st.metric("Subscribers", f"{int(info1['subscriber_count']):,}")
        st.metric("Total Views", f"{int(info1['view_count']):,}")
        st.metric("Total Videos", f"{int(info1['video_count']):,}")
        
        st.markdown(f"**Published At:** {info1['published_at']}")
        st.divider()
        if data1:
         df = pd.DataFrame(data1)  

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
        df = pd.DataFrame(data1)

        st.subheader("📊 Likes and Comments per Video")

            # Create chart dataframe using actual video title
        chart_df = df[["title", "like_count", "comment_count"]].copy()

            # Base chart
        base = alt.Chart(chart_df).encode(
                x=alt.X("title:N", title="Video Title", sort=None)
            )

            # Likes line
        likes_line = base.mark_line(
                color="#FF0000",
                size=3
            ).encode(
                y=alt.Y("like_count:Q", title="Count"),
                tooltip=["title", "like_count"]
            )

            # Comments line
        comments_line = base.mark_line(
                color="#8B0000",
                size=3
            ).encode(
                y=alt.Y("comment_count:Q"),
                tooltip=["title", "comment_count"]
            )

            # Rotate labels so they don’t overlap
        final_chart = (likes_line + comments_line).properties(
                height=400
            ).configure_axisX(
                labelAngle=-45
            )
        

        df = pd.DataFrame(data1)

        try:
            average_views = float(df["view_count"].mean())
            total_subscribers = int(info1["subscriber_count"])
            subscriber_watch_percent = (
                (average_views / total_subscribers) * 100
                if total_subscribers > 0 else 0
            )
        except (ValueError, TypeError):
            subscriber_watch_percent = 0
        st.altair_chart(final_chart, use_container_width=True)


        st.subheader("👥 Subscriber Watch Percentage")  
        st.divider()
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
        st.divider()
        st.subheader("🔥 Upload Frequency Analysis")

        try:
            total_videos = int(info1["video_count"])
            published_date = datetime.strptime(info1["published_at"][:10], "%Y-%m-%d").date()
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

        

        
        st.metric("Creator Type", creator_type)

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



       



        
       

    with col2:
        st.subheader(f"📌 {info2['channel_name']}")
        st.metric("Subscribers", f"{int(info2['subscriber_count']):,}")
        st.metric("Total Views", f"{int(info2['view_count']):,}")
        st.metric("Total Videos", f"{int(info2['video_count']):,}")
        st.markdown(f"**Published At:** {info2['published_at']}")
        st.divider()
        if data2:
         df = pd.DataFrame(data2)  

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
        df = pd.DataFrame(data2)

        st.subheader("📊 Likes and Comments per Video")

            # Create chart dataframe using actual video title
        chart_df = df[["title", "like_count", "comment_count"]].copy()

            # Base chart
        base = alt.Chart(chart_df).encode(
                x=alt.X("title:N", title="Video Title", sort=None)
            )

            # Likes line
        likes_line = base.mark_line(
                color="#FF0000",
                size=3
            ).encode(
                y=alt.Y("like_count:Q", title="Count"),
                tooltip=["title", "like_count"]
            )

            # Comments line
        comments_line = base.mark_line(
                color="#8B0000",
                size=3
            ).encode(
                y=alt.Y("comment_count:Q"),
                tooltip=["title", "comment_count"]
            )

            # Rotate labels so they don’t overlap
        final_chart = (likes_line + comments_line).properties(
                height=400
            ).configure_axisX(
                labelAngle=-45
            )

        st.altair_chart(final_chart, use_container_width=True)
        df = pd.DataFrame(data2)

        try:
            average_views = float(df["view_count"].mean())
            total_subscribers = int(info2["subscriber_count"])
            subscriber_watch_percent = (
                (average_views / total_subscribers) * 100
                if total_subscribers > 0 else 0
            )
        except (ValueError, TypeError):
            subscriber_watch_percent = 0
        st.divider()
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

        st.plotly_chart(fig_subs, use_container_width=True, key="subs_watch_2")
        st.divider()
        st.subheader("🔥 Upload Frequency Analysis")

        try:
            total_videos = int(info2["video_count"])
            published_date = datetime.strptime(info2["published_at"][:10], "%Y-%m-%d").date()
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

        
        st.metric("Creator Type", creator_type)

        # Gauge
        fig_freq = go.Figure(go.Indicator(
            mode="gauge+number",
            value=upload_frequency,
            title={"text": "Uploads per Month"},
            gauge={
                "axis": {"range": [0, 30]},
                "bar": {"color": "red"},
                "steps": [
                        {"range": [0, 6], "color": "#ffcccc"},
                        {"range": [6, 12], "color": "#ff9999"},
                        {"range": [12, 18], "color": "#ff6666"},
                        {"range": [18, 24], "color": "#ff3333"},
                        {"range": [24, 30], "color": "#cc0000"},
                ],
            }
        ))

        fig_freq.update_layout(
            margin=dict(l=10, r=10, t=80, b=10),
            height=300,
        )

        st.plotly_chart(fig_freq, use_container_width=True, key="upload_freq_2")
    st.divider()    
    st.title("More features are Under Development! 🚧 Stay Tuned....................! ")       



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