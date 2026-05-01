import streamlit as st
from streamlit_lottie import st_lottie
from services import load_lottieurl

st.set_page_config(
    page_title="InsightTube - Smart YouTube Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- Theme State --------------------
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

theme = st.session_state.theme

if theme == 'dark':
    bg_color = '#0b0f19'
    text_color = '#f1f5f9'
    sidebar_bg = '#111827'
    border_color = '#1f2937'
    card_bg = 'rgba(30, 41, 59, 0.6)'
    card_hover = 'rgba(30, 41, 59, 0.9)'
    step_bg = '#1e293b'
    subtitle_color = '#94A3B8'
    title_color = '#F8FAFC'
else:
    bg_color = '#f8fafc'
    text_color = '#0f172a'
    sidebar_bg = '#f1f5f9'
    border_color = '#e2e8f0'
    card_bg = 'rgba(255, 255, 255, 0.8)'
    card_hover = 'rgba(255, 255, 255, 1)'
    step_bg = '#ffffff'
    subtitle_color = '#475569'
    title_color = '#0f172a'

# -------------------- Top Right Toggle --------------------
t_col1, t_col2 = st.columns([15, 1])
with t_col2:
    if st.button("☀️" if theme == 'dark' else "🌙"):
        st.session_state.theme = 'light' if theme == 'dark' else 'dark'
        st.rerun()

# -------------------- CSS Styling --------------------
css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    /* Global Typography & Colors */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: __BG_COLOR__;
        color: __TEXT_COLOR__;
    }

    /* Hide Default Navigation */
    [data-testid="stSidebarNav"] { display: none; }
    
    /* Sidebar Modernization */
    [data-testid="stSidebar"] {
        background-color: __SIDEBAR_BG__ !important;
        border-right: 1px solid __BORDER_COLOR__;
    }
    
    .sidebar-logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 0 20px 0;
    }
    .sidebar-logo-text {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3B82F6, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Hero Section */
    .hero-container {
        text-align: left;
        padding: 15px 0 20px 0;
        background: none;
        animation: fadeIn 0.8s ease-out forwards;
    }
    .hero-title {
        font-size: 3.8rem !important;
        font-weight: 800 !important;
        line-height: 1.15;
        margin-bottom: 20px !important;
        background: linear-gradient(135deg, #93C5FD 0%, #C4B5FD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% 200%;
        animation: gradientBG 6s ease infinite;
    }
    .hero-subtitle {
        font-size: 1.25rem !important;
        color: __SUBTITLE_COLOR__ !important;
        font-weight: 400 !important;
        max-width: 600px;
        margin-bottom: 40px !important;
        line-height: 1.6;
    }

    /* Buttons Override */
    .stButton > button {
        border-radius: 50px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3B82F6 0%, #6366F1 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5) !important;
    }
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        color: #f1f5f9 !important;
        border: 1px solid #475569 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: #94A3B8 !important;
        transform: translateY(-3px) !important;
    }

    /* SaaS Cards / Glassmorphism */
    .glass-card {
        background: __CARD_BG__;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 30px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        animation: fadeIn 0.8s ease-out forwards;
    }
    .glass-card:hover {
        transform: translateY(-8px);
        background: __CARD_HOVER__;
        border-color: rgba(96, 165, 250, 0.3);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 20px rgba(59, 130, 246, 0.1);
    }
    
    .card-icon {
        font-size: 2.5rem;
        margin-bottom: 20px;
        display: inline-block;
        padding: 15px;
        border-radius: 16px;
        background: rgba(59, 130, 246, 0.1);
    }
    .card-title {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        color: __TITLE_COLOR__ !important;
        margin-bottom: 12px !important;
    }
    .card-desc {
        color: __SUBTITLE_COLOR__ !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }

    /* Section Headers */
    .section-header {
        text-align: center;
        margin: 80px 0 50px;
        animation: fadeIn 0.8s ease-out forwards;
    }
    .section-tag {
        color: #3B82F6;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        font-size: 0.85rem;
        margin-bottom: 10px;
        display: block;
    }
    .section-title {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: __TITLE_COLOR__ !important;
        margin: 0 !important;
    }

    /* How It Works - Horizontal Flow */
    .timeline-container {
        display: flex;
        justify-content: space-between;
        gap: 20px;
        margin-top: 40px;
        flex-wrap: wrap;
    }
    .timeline-step {
        flex: 1;
        min-width: 220px;
        background: __STEP_BG__;
        padding: 30px;
        border-radius: 16px;
        position: relative;
        border-top: 4px solid #3B82F6;
        transition: transform 0.3s ease;
    }
    .timeline-step:hover {
        transform: translateY(-5px);
    }
    .step-number {
        position: absolute;
        top: -20px;
        left: 30px;
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #3B82F6 0%, #6366F1 100%);
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.2rem;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.4);
    }
    .step-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: __TITLE_COLOR__;
        margin: 15px 0 10px;
    }
    .step-desc {
        color: __SUBTITLE_COLOR__;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 40px 20px;
        margin-top: 80px;
        border-top: 1px solid __BORDER_COLOR__;
        color: #64748b;
    }
    .footer-brand {
        font-weight: 700;
        color: __TITLE_COLOR__;
        font-size: 1.2rem;
    }
    .footer-links a {
        color: #3B82F6;
        text-decoration: none;
        margin: 0 10px;
    }
    .footer-links a:hover {
        text-decoration: underline;
    }

    /* Streamlit specific overrides */
    hr { border-color: __BORDER_COLOR__ !important; }
</style>
"""

css = css.replace('__BG_COLOR__', bg_color)
css = css.replace('__TEXT_COLOR__', text_color)
css = css.replace('__SIDEBAR_BG__', sidebar_bg)
css = css.replace('__BORDER_COLOR__', border_color)
css = css.replace('__SUBTITLE_COLOR__', subtitle_color)
css = css.replace('__CARD_BG__', card_bg)
css = css.replace('__CARD_HOVER__', card_hover)
css = css.replace('__TITLE_COLOR__', title_color)
css = css.replace('__STEP_BG__', step_bg)

st.markdown(css, unsafe_allow_html=True)

# -------------------- Sidebar Navigation --------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo-container">
        <img src="https://cdn-icons-png.flaticon.com/512/1384/1384060.png" width="45">
        <h3 class="sidebar-logo-text">InsightTube</h3>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/10307/10307931.png", width=40)
    col2.page_link("Home.py", label="Home")
    
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/404/404672.png", width=40)
    col2.page_link("pages/1_Channel_Analysis.py", label="Channel Analysis")
    
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/2593/2593453.png", width=40)
    col2.page_link("pages/5_Sentiment_Analysis.py", label="Sentiment Analysis")
    
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/934/934478.png", width=40)
    col2.page_link("pages/2_Channel_Compare.py", label="Channel Compare")
    
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/9227/9227001.png", width=40)
    col2.page_link("pages/4_Trending.py", label="Trending Videos")
    
    col1, col2 = st.columns([1, 8])
    col1.image("https://cdn-icons-png.flaticon.com/128/9985/9985768.png", width=40)
    col2.page_link("pages/3_About_Us.py", label="About Us")

# -------------------- Hero Section --------------------
hero_col1, hero_col2 = st.columns([1.2, 1], gap="large")

with hero_col1:
    st.markdown("""
    <div class="hero-container">
        <h2 style="color: #60A5FA; font-weight: 700; font-size: 1.6rem; margin-bottom: 5px; letter-spacing: 0px;">InsightTube</h2>
        <h1 class="hero-title">Turn YouTube Data into Actionable Insights</h1>
        <p class="hero-subtitle">
            Empower your content strategy with deep analytics, sentiment tracking, and competitor benchmarking. 
            Built for creators, agencies, and brands who want to dominate the YouTube algorithm.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons
    b1, b2, _ = st.columns([1, 1, 1.5])
    with b1:
        if st.button("🚀 Get Started", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Channel_Analysis.py")
    with b2:
        if st.button("▶️ View Demo", use_container_width=True, type="secondary"):
            st.switch_page("pages/5_Sentiment_Analysis.py")

with hero_col2:
    import base64
    import os
    
    img_path = "background.png"
    img_html = ""
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        img_html = f'<img src="data:image/png;base64,{b64}" style="width: 100%; display: block; transform: scale(1.05);">'
    else:
        img_html = '<img src="https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?q=80&w=1000&auto=format&fit=crop" style="width: 100%; display: block; filter: brightness(0.9);">'

    st.markdown(f"""
    <div style="border-radius: 20px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.4); margin-top: 15px; border: 1px solid rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; background: #0b0f19;">
        {img_html}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# -------------------- Core Features (3x2 Grid) --------------------
st.markdown("""
<div class="section-header">
    <span class="section-tag">Powerful Capabilities</span>
    <h2 class="section-title">Everything you need to grow</h2>
</div>
""", unsafe_allow_html=True)

f_col1, f_col2, f_col3 = st.columns(3, gap="medium")

with f_col1:
    st.markdown("""
    <div class="glass-card">
        <span class="card-icon">📊</span>
        <h3 class="card-title">Channel Analytics</h3>
        <p class="card-desc">Track subscriber growth, view counts, and engagement trends. Uncover exactly what metrics drive your channel forward.</p>
    </div>
    """, unsafe_allow_html=True)

with f_col2:
    st.markdown("""
    <div class="glass-card">
        <span class="card-icon">🧠</span>
        <h3 class="card-title">AI Sentiment Analysis</h3>
        <p class="card-desc">Process thousands of comments instantly with Llama 3.1. Detect sarcasm, emojis, and true audience sentiment at scale.</p>
    </div>
    """, unsafe_allow_html=True)

with f_col3:
    st.markdown("""
    <div class="glass-card">
        <span class="card-icon">⚔️</span>
        <h3 class="card-title">Competitor Compare</h3>
        <p class="card-desc">Benchmarking made easy. Compare your performance side-by-side with your biggest rivals to find content gaps.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
f_col4, f_col5, f_col6 = st.columns(3, gap="medium")

with f_col4:
    st.markdown("""
    <div class="glass-card">
        <span class="card-icon">🔥</span>
        <h3 class="card-title">Trending Discoveries</h3>
        <p class="card-desc">Monitor what's going viral across YouTube right now. Analyze top trending videos by region and category.</p>
    </div>
    """, unsafe_allow_html=True)

with f_col5:
    st.markdown("""
    <div class="glass-card">
        <span class="card-icon">📈</span>
        <h3 class="card-title">Beautiful Visuals</h3>
        <p class="card-desc">Export-ready, interactive Plotly charts. Present your data beautifully to sponsors, teams, or stakeholders.</p>
    </div>
    """, unsafe_allow_html=True)

with f_col6:
    st.markdown("""
    <div class="glass-card">
        <span class="card-icon">⚡</span>
        <h3 class="card-title">Real-time Data</h3>
        <p class="card-desc">Directly integrated with the official YouTube Data API v3 for 100% accurate, up-to-the-minute statistics.</p>
    </div>
    """, unsafe_allow_html=True)


# -------------------- How It Works --------------------
st.markdown("""
<div class="section-header">
    <span class="section-tag">Simple Process</span>
    <h2 class="section-title">How InsightTube Works</h2>
</div>

<div class="timeline-container">
    <div class="timeline-step">
        <div class="step-number">1</div>
        <h4 class="step-title">Input Target</h4>
        <p class="step-desc">Enter any public YouTube channel name, video URL, or creator handle.</p>
    </div>
    <div class="timeline-step">
        <div class="step-number">2</div>
        <h4 class="step-title">Fetch Data</h4>
        <p class="step-desc">We securely query the YouTube API for the latest metrics, videos, and comments.</p>
    </div>
    <div class="timeline-step">
        <div class="step-number">3</div>
        <h4 class="step-title">AI Processing</h4>
        <p class="step-desc">Advanced NLP models categorize sentiments, keywords, and extract key themes.</p>
    </div>
    <div class="timeline-step">
        <div class="step-number">4</div>
        <h4 class="step-title">Visualize</h4>
        <p class="step-desc">Explore your beautifully tailored dashboards and make data-driven decisions.</p>
    </div>
</div>
""", unsafe_allow_html=True)


# -------------------- Footer --------------------
st.markdown("""
<div class="footer">
    <div class="footer-brand">InsightTube</div>
    <p>Smart YouTube Analytics for Modern Creators</p>
    <div class="footer-links">
        <a href="https://github.com/Pbo7" target="_blank">GitHub Repository</a> • 
        <a href="#">Documentation</a> • 
        <a href="#">API Status</a>
    </div>
    <p style="margin-top: 20px; font-size: 0.85rem; color: #475569;">© 2026 InsightTube Inc. Built with Python & Streamlit.</p>
</div>
""", unsafe_allow_html=True)