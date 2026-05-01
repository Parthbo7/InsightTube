from pyparsing import col
import streamlit as st
import base64
import os

st.set_page_config(
    page_title="InsightTube - Smart YouTube Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- Load Background Image --------------------
# Try to load from multiple possible locations
possible_paths = [
    'ChatGPT_Image_Mar_12__2026__09_22_51_PM.png',
    'background.png',
    './background.png',
]

bg_image_uri = None
for path in possible_paths:
    if os.path.exists(path):
        with open(path, 'rb') as img_file:
            bg_image_data = base64.b64encode(img_file.read()).decode('utf-8')
            bg_image_uri = f"data:image/png;base64,{bg_image_data}"
        break

# Fallback to Imgbb if local file not found
if not bg_image_uri:
    bg_image_uri = "url('https://i.ibb.co/yFL0vk0h/background.png')"
else:
    bg_image_uri = f"url('{bg_image_uri}')"

# -------------------- Hide Default Sidebar Navigation --------------------
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- Global Styling & Background --------------------
st.markdown("""
<style>
    /* Background Image - Only for App */
    .stApp {
        background-color: #0f172a;
    }
    
    /* Remove Streamlit padding from hero sections */
    .block-container [data-testid="stMarkdownContainer"]:has(.hero-top),
    .block-container [data-testid="stMarkdownContainer"]:has(.hero-tagline-section),
    .block-container [data-testid="stMarkdownContainer"]:has(.hero-background) {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Hero Top - Title Section */
    .hero-top {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.95) 100%);
        text-align: center;
        padding: 50px 20px 15px;
        margin: 0;
        width: 100%;
    }
    
    /* Hero Tagline - Just Above Image */
    .hero-tagline-section {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.95) 100%);
        text-align: center;
        padding: 10px 20px 10px;
        margin: 0;
        width: 100%;
    }
    
    /* Hero Section with Background Image */
    .hero-background {
        background-image: __BG_IMAGE__;
        background-size: cover;
        background-position: center;
        background-attachment: scroll;
        background-repeat: no-repeat;
        margin: 0;
        padding: 0;
        margin-bottom: 20px;
        height: 500px;
        width: 100%;
    }
    
    /* Main container */
    .block-container {
        max-width: 100%;
        padding: 0;
        margin: 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.95) 100%) !important;
        backdrop-filter: none !important;
        border-right: 1px solid rgba(148, 163, 184, 0.2) !important;
    }
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6 {
        color: #F1F5F9 !important;
        font-weight: 700 !important;
    }
    
    p, span, label {
        color: #E2E8F0 !important;
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center;
    }
    
    .hero-title {
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        margin-bottom: 10px !important;
        margin-top: 0 !important;
        background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 1.1rem !important;
        color: #CBD5E1 !important;
        font-weight: 400 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 16px;
        padding: 28px;
        backdrop-filter: none;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        cursor: pointer;
    }
    
    .feature-card:hover {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.98) 100%);
        border-color: rgba(96, 165, 250, 0.5);
        transform: translateY(-8px);
        box-shadow: 0 16px 48px rgba(59, 130, 246, 0.3);
    }
    
    .card-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
        display: block;
    }
    
    .card-title {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
        color: #F1F5F9 !important;
    }
    
    .card-description {
        font-size: 0.95rem !important;
        color: #CBD5E1 !important;
        line-height: 1.6 !important;
        margin: 0 !important;
    }
    
    /* Divider */
    hr {
        background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.3), transparent) !important;
        border: none !important;
        height: 1px !important;
        margin: 3rem 0 !important;
    }
    
    /* Section Title */
    .section-title {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        margin-bottom: 35px !important;
        color: #F1F5F9 !important;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .section-icon {
        font-size: 2rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #6366F1 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Info boxes */
    .stInfo {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%) !important;
        border-left: 4px solid #3B82F6 !important;
        border-radius: 10px !important;
        backdrop-filter: none !important;
    }
    
    /* Steps styling */
    .step-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%);
        border-left: 4px solid #60A5FA;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        backdrop-filter: none;
    }
    
    .step-number {
        display: inline-block;
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #3B82F6 0%, #6366F1 100%);
        border-radius: 50%;
        text-align: center;
        line-height: 40px;
        color: white;
        font-weight: 700;
        margin-right: 12px;
        vertical-align: middle;
    }
    
    /* Link styling */
    a {
        color: #60A5FA !important;
        text-decoration: none !important;
    }
    
    a:hover {
        color: #93C5FD !important;
        text-decoration: underline !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem !important;
        }
        
        .hero-subtitle {
            font-size: 1.2rem !important;
        }
        
        .section-title {
            font-size: 1.8rem !important;
        }
    }
</style>
""".replace('__BG_IMAGE__', bg_image_uri), unsafe_allow_html=True)

# -------------------- Sidebar Navigation --------------------
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

# -------------------- Hero Section --------------------
st.markdown("""
<div class="hero-top">
    <h1 class="hero-title">InsightTube</h1>
</div>
<div class="hero-tagline-section">
    <p class="hero-subtitle">Generate Smart Insights from YouTube Channels</p>
</div>
<div class="hero-background">
</div>
""", unsafe_allow_html=True)

st.divider()

# -------------------- Quick Access Buttons --------------------
st.markdown("<h3 style='text-align: center; margin-bottom: 30px;'>⚡ Get Started</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Channel Analysis", use_container_width=True, key="btn_channel"):
        st.switch_page("pages/1_Channel_Analysis.py")

with col2:
    if st.button("⚔️ Compare Channels", use_container_width=True, key="btn_compare"):
        st.switch_page("pages/2_Channel_Compare.py")

col3, col4 = st.columns(2)

with col3:
    if st.button("🔥 Trending Videos", use_container_width=True, key="btn_trending"):
        st.switch_page("pages/4_Trending.py")

with col4:
    if st.button("🌍 About Us", use_container_width=True, key="btn_about"):
        st.switch_page("pages/3_About_Us.py")

col5, col6 = st.columns(2)

with col5:
    if st.button("💬 Sentiment Analysis", use_container_width=True, key="btn_sentiment"):
        st.switch_page("pages/5_Sentiment_Analysis.py")

st.divider()

# -------------------- Core Features Section --------------------
st.markdown("""
<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 35px;">
    <span style="font-size: 2.5rem;">🎯</span>
    <h2 class="section-title" style="margin: 0;">Core Features</h2>
</div>
""", unsafe_allow_html=True)

# Feature cards in a 2x2 grid
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <span class="card-icon">📊</span>
        <div class="card-title">Channel Analysis</div>
        <p class="card-description">Analyze subscriber growth, views, engagement metrics, and performance trends in detailed dashboards.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <span class="card-icon">⚔️</span>
        <div class="card-title">Channel Compare</div>
        <p class="card-description">Compare performance metrics between two channels side by side and identify competitive advantages.</p>
    </div>
    """, unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    <div class="feature-card">
        <span class="card-icon">🔥</span>
        <div class="card-title">Trending Videos</div>
        <p class="card-description">Discover popular content across YouTube categories and understand what makes videos go viral.</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <span class="card-icon">📈</span>
        <div class="card-title">Data Visualization</div>
        <p class="card-description">Interactive charts, graphs, and analytics insights with advanced filtering and export capabilities.</p>
    </div>
    """, unsafe_allow_html=True)

col5, col6 = st.columns(2)

with col5:
    st.markdown("""
    <div class="feature-card">
        <span class="card-icon">💬</span>
        <div class="card-title">Comment Sentiment Analysis</div>
        <p class="card-description">Understand what your audience truly feels. Analyze comment tone with TextBlob or Google Gemini AI — supports Hinglish, sarcasm, and emojis.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# -------------------- How It Works Section --------------------
st.markdown("""
<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 35px;">
    <span style="font-size: 2.5rem;">⚙️</span>
    <h2 class="section-title" style="margin: 0;">How It Works</h2>
</div>
""", unsafe_allow_html=True)

steps = [
    ("1️⃣", "Enter a YouTube Channel", "Search for any creator and enter their channel name to begin analysis."),
    ("2️⃣", "Data Fetched via API", "Real-time data is retrieved using the YouTube Data API v3 for accurate analytics."),
    ("3️⃣", "Advanced Processing", "Data is processed using Python and Pandas for deep analysis and calculations."),
    ("4️⃣", "Visualize Insights", "Beautiful, interactive dashboards showcase insights with advanced analytics tools.")
]

for number, title, description in steps:
    st.markdown(f"""
    <div class="step-container">
        <span style="font-size: 1.8rem; vertical-align: middle;">{number}</span>
        <strong style="color: #F1F5F9; font-size: 1.1rem; vertical-align: middle; margin-left: 10px;">{title}</strong>
        <p style="color: #CBD5E1; margin: 10px 0 0 0;">{description}</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# -------------------- YouTube Channel Section --------------------
st.markdown("""
<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 35px;">
    <span style="font-size: 2.5rem;">🔗</span>
    <h2 class="section-title" style="margin: 0;">Find Your Channel</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<p style="color: #E2E8F0; font-size: 1.1rem; margin-bottom: 20px;">
    Can't remember your exact channel name? Click below to visit YouTube and search for it.
</p>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.link_button("🔗 Open YouTube", "https://www.youtube.com", use_container_width=True)

st.divider()