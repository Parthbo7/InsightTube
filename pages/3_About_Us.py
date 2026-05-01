import streamlit as st
from streamlit_lottie import st_lottie
from services import load_lottieurl
from supabase import create_client

st.set_page_config(
    page_title="InsightTube - About Us",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialization for Supabase
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(supabase_url, supabase_key)
except:
    import os
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    supabase = create_client(supabase_url, supabase_key) if supabase_url else None

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
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.about-card {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    border-left: 4px solid #3B82F6;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
}
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
    z-index: 999;
}
</style>
""", unsafe_allow_html=True)

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
    col1,col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/2593/2593453.png", width=40)
    col2.page_link("pages/5_Sentiment_Analysis.py", label="Sentiment Analysis")

# -------------------- Page Header --------------------
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
        <div style="display:flex; align-items:center; gap:15px; margin-top:20px;">
            <img src="https://cdn-icons-png.flaticon.com/128/9985/9985768.png" width="60">
            <h1 style="margin:0; font-size: 3rem;">About Us</h1>
        </div>
        <p style="font-size: 1.2rem; color: #94A3B8; margin-top: 15px;">
            InsightTube is a smart YouTube analytics platform that allows users to analyze and explore detailed insights about any YouTube channel. It helps users understand channel performance, trending videos, engagement metrics, and growth patterns through an easy-to-use dashboard.
        </p>
    """, unsafe_allow_html=True)
with col2:
    lottie_about = load_lottieurl("https://lottie.host/e2d46e38-16dc-4fc6-b51f-506079c656d0/BfRzF2nBIt.json")
    if lottie_about:
        st_lottie(lottie_about, height=250, key="about_anim")

st.divider()

# -------------------- Tabs for Content --------------------
tab1, tab2, tab3 = st.tabs(["🚀 Project Overview", "👨‍💻 Creator", "💡 Feedback"])

with tab1:
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown("""
        <div class="about-card">
            <h3><img src="https://cdn-icons-png.flaticon.com/128/10050/10050724.png" width="30" style="vertical-align:middle; margin-right:10px;"> Platform Overview</h3>
            <p style="color: #CBD5E1;">InsightTube is a data analytics platform that helps users explore YouTube performance insights. Developed as part of the <strong>Infosys Springboard Internship Program</strong>, it demonstrates practical implementation of data analytics dashboards, API integration, and real-world analytics applications.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="about-card">
            <h3><img src="https://cdn-icons-png.flaticon.com/128/17047/17047745.png" width="30" style="vertical-align:middle; margin-right:10px;"> Key Metrics</h3>
            <div style="display:flex; justify-content: space-around; margin-top:15px;">
                <div style="text-align:center;">
                    <h2 style="color:#3B82F6; margin:0;">4</h2>
                    <p style="color:#94A3B8;">Modules</p>
                </div>
                <div style="text-align:center;">
                    <h2 style="color:#10B981; margin:0;">10+</h2>
                    <p style="color:#94A3B8;">Charts</p>
                </div>
                <div style="text-align:center;">
                    <h2 style="color:#F59E0B; margin:0;">1</h2>
                    <p style="color:#94A3B8;">API Integration</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="about-card">
            <h3><img src="https://cdn-icons-png.flaticon.com/128/4413/4413567.png" width="30" style="vertical-align:middle; margin-right:10px;"> Technologies Used</h3>
            <ul style="color: #CBD5E1; line-height: 1.8;">
                <li><strong>Frontend:</strong> Streamlit, HTML/CSS</li>
                <li><strong>Backend:</strong> Python</li>
                <li><strong>Database:</strong> SQL, Supabase, Postgres</li>
                <li><strong>Data Processing:</strong> Pandas, NumPy</li>
                <li><strong>Visualization:</strong> Plotly</li>
                <li><strong>API:</strong> YouTube Data API v3</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="about-card">
            <h3><img src="https://cdn-icons-png.flaticon.com/128/13163/13163215.png" width="30" style="vertical-align:middle; margin-right:10px;"> Future Enhancements</h3>
            <ul style="color: #CBD5E1; line-height: 1.8;">
                <li>AI based content strategy recommendations</li>
                <li>Channel growth prediction</li>
                <li>Revenue estimation tools</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    col_img, col_info = st.columns([1, 2], gap="large")
    with col_img:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=250)
    with col_info:
        st.markdown("""
        <h2 style="margin-bottom: 5px;">Parth Pandurang Bulbule</h2>
        <h4 style="color: #3B82F6; margin-top: 0;">Engineering Student | Information Technology</h4>
        <p style="color: #94A3B8;">@Mahatma Gandhi Mission's College of Engineering, Nanded</p>
        
        <p style="font-size: 1.1rem; line-height: 1.6; color: #CBD5E1;">
        I am passionate about building intelligent systems that solve real-world problems. With a strong interest in analytics, AI, and software development, I focus on creating structured, efficient, and scalable solutions.
        <br><br>
        InsightTube was built as a step toward mastering data systems, API integrations, and analytics architecture — combining engineering logic with digital creativity.
        </p>
        
        <div style="display: flex; gap: 15px; margin-top: 25px;">
            <a href="https://www.linkedin.com/in/parth-bulbule/" target="_blank">
                <button style="background-color: #0A66C2; color: white; padding: 10px 20px; border: none; border-radius: 8px; font-weight:bold; cursor: pointer;">
                    🔗 LinkedIn
                </button>
            </a>
            <a href="https://www.instagram.com/parthbo.7/?utm_source=qr&r=nametag" target="_blank">
                <button style="background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); color: white; padding: 10px 20px; border: none; border-radius: 8px; font-weight:bold; cursor: pointer;">
                    📸 Instagram
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div style="background-color: #1f2937; padding: 30px; border-radius: 12px; border-top: 4px solid #F59E0B;">
        <h3 style="margin-top:0;"><img src="https://cdn-icons-png.flaticon.com/128/7119/7119415.png" width="30" style="vertical-align:middle; margin-right:10px;"> We'd Love to Hear From You!</h3>
        <p style="color: #94A3B8; margin-bottom: 25px;">Have suggestions or feedback to improve InsightTube? Drop us a message below.</p>
    """, unsafe_allow_html=True)
    
    with st.form("feedback_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        message = st.text_area("Your Idea / Feedback", height=150)
        submitted = st.form_submit_button("Submit Feedback", type="primary")
        
        if submitted:
            if supabase:
                data = {"name": name, "email": email, "message": message}
                try:
                    supabase.table("ideas_feedback").insert(data).execute()
                    st.success("Thanks! Your feedback was submitted successfully.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Failed to submit feedback: {e}")
            else:
                st.warning("Database connection is not configured. Feedback cannot be saved currently.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    © 2026 InsightTube | Built with Streamlit 💙 | Pbo7
</div>
""", unsafe_allow_html=True)
