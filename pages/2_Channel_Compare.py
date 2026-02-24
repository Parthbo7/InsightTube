import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
    st.markdown("## 📊 InsightTube")
    st.divider()

    st.page_link("Home.py", label="🏠 Home")
    st.page_link("pages/1_Channel_Analysis.py", label="📊 Channel Analysis")
    st.page_link("pages/2_Channel_Compare.py", label="⚔️ Channel Compare")
    st.page_link("pages/3_About_Us.py", label="🌍 About Us")

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
st.title("⚔️ Channel Comparison")
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

        info1, data1 = run_full_channel_analysis(channel_1_input)
        info2, data2 = run_full_channel_analysis(channel_2_input)

        if info1 and info2:
            st.session_state["info1"] = info1
            st.session_state["data1"] = data1
            st.session_state["info2"] = info2
            st.session_state["data2"] = data2

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
    




st.divider()
st.caption("© 2026 InsightTube | Built with Streamlit 💙")
