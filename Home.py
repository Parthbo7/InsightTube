from pyparsing import col
import streamlit as st

st.set_page_config(page_title="InsightTube", layout="wide")
st.divider()
col1,col2 = st.columns([1,10])
col1.image("https://cdn-icons-png.flaticon.com/512/1384/1384060.png", width=80)
col2.title(" InsightTube")
st.markdown("### Smart YouTube Analytics Platform")
st.divider()

st.write("Welcome to your YouTube Analytics Dashboard 🚀")

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
    st.page_link("pages/4_Trending.py", label="🔥 Trending Videos")
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


# -------------------- Action Buttons --------------------
col1, col2, col3,col4 = st.columns(4)

with col1:
    if st.button("📊 Channel Analysis", use_container_width=True):
        st.switch_page("pages/1_Channel_Analysis.py")

with col2:
    if st.button("⚔️ Compare Channels", use_container_width=True):
        st.switch_page("pages/2_Channel_Compare.py")

with col3:
    if st.button("🔥 Trending Videos", use_container_width=True):
        st.switch_page("pages/4_Trending.py")

with col4:
    if st.button("🌍 About Us", use_container_width=True):
        st.switch_page("pages/3_About_Us.py")


# -------------------- Info Section --------------------
st.divider()
col1, col2 = st.columns([1,15])
col1.image("https://cdn-icons-png.flaticon.com/128/2140/2140212.png", width=50)
col2.subheader(" Core Features")

col1, col2 = st.columns(2)

with col1:
    st.info("📊 **Channel Analysis**\n\nAnalyze subscriber growth, views, and engagement.")

    st.info("🔥 **Trending Videos**\n\nDiscover popular content across YouTube categories.")

with col2:
    st.info("⚔ **Channel Compare**\n\nCompare performance between two channels.")

    st.info("📈 **Data Visualization**\n\nInteractive charts and analytics insights.")

st.divider()
col1,col2 = st.columns([1,15])
col1.image("https://cdn-icons-gif.flaticon.com/17122/17122416.gif", width=50)
col2.subheader(" How It Works")

st.markdown("""
1️⃣ Enter a YouTube channel name  
2️⃣ Data is fetched using the YouTube Data API  
3️⃣ Data is processed using Python and Pandas  
4️⃣ Insights are visualized using interactive charts  
""")
st.divider()
col1,col2 = st.columns([1,15])
col1.image("https://cdn-icons-gif.flaticon.com/16678/16678143.gif", width=50)
col2.subheader(" Find Your YouTube Channel")

youtube_url = "https://www.youtube.com"

st.link_button("Open YouTube", youtube_url)
st.write(
"Can't remember the exact name of your channel? "
"Click the button below to go to YouTube and search for your channel."
)

st.divider()

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

st.markdown("""
<style>

.footer-container {
    background-color: #0b0f19;
    padding: 40px 60px;
    border-top: 1px solid #2a2a2a;
    margin-top: 60px;
}

.footer-bottom {
    border-top: 1px solid #2a2a2a;
    margin-top: 30px;
    padding-top: 15px;
    text-align: center;
    font-size: 14px;
    color: #9aa0a6;
}

.footer-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 10px;
}

.footer-link {
    color: #58a6ff;
    text-decoration: none;
}

.footer-link:hover {
    text-decoration: underline;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="footer-container">

<div style="display:flex; justify-content:space-between; flex-wrap:wrap;">

<div>
<div class="footer-title">📊 InsightTube</div>
<p>Smart YouTube Analytics Platform</p>
</div>

<div>
<div class="footer-title">🔗 Navigation</div>

<p><a class="footer-link" href="/">🏠 Home</a></p>

<p><a class="footer-link" href="/Channel_Analysis">📊 Channel Analysis</a></p>

<p><a class="footer-link" href="/Channel_Compare">⚔ Channel Compare</a></p>

<p><a class="footer-link" href="/Trending_Videos">🔥 Trending Videos</a></p>

<p><a class="footer-link" href="/About_Us">🌍 About Us</a></p>

</div>

<div>
<div class="footer-title">🌍 Connect</div>

<p><a class="footer-link" href="https://linkedin.com">LinkedIn</a></p>
<p><a class="footer-link" href="https://instagram.com">Instagram</a></p>
<p><a class="footer-link" href="https://github.com">GitHub</a></p>

</div>

</div>

<div class="footer-bottom">
© 2026 InsightTube | Built with Streamlit | Internship Project | Pbo7
</div>

</div>
""", unsafe_allow_html=True)