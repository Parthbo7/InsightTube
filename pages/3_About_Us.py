import streamlit as st
from supabase import create_client
st.set_page_config(layout="wide")
st.divider()
col1,col2 = st.columns([1,10])
col1.image("https://cdn-icons-png.flaticon.com/128/9985/9985768.png", width=80)
col2.title("About Us")
st.divider()
st.set_page_config(
    page_title="InsightTube",
    layout="wide",
    initial_sidebar_state="expanded"
)
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = create_client(supabase_url, supabase_key)
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

st.set_page_config(page_title="About Us", page_icon="🚀")

st.write("InsightTube is a smart YouTube analytics platform that allows users to analyze and explore detailed insights about any YouTube channel. It helps users understand channel performance, trending videos, engagement metrics, and growth patterns through an easy-to-use dashboard. The platform provides valuable data that helps creators and viewers better understand content performance and audience behavior.")
st.divider()

st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/10050/10050724.png" width="45">
            <h3 style="margin:0;">Project Overview</h3>
        </div>
        """, unsafe_allow_html=True)


st.markdown("""
InsightTube is a data analytics platform that helps users explore YouTube performance insights.

**Core Features**

• Channel Analytics Dashboard  
• Channel Comparison  
• Trending Video Discovery  
• Engagement & Performance Metrics  
• Data Visualization using interactive charts
""")
st.divider()
st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/17772/17772829.png" width="45">
            <h3 style="margin:0;">Internship Project</h3>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
This project was developed as part of the **Infosys Springboard Internship Program**.

The goal of this project is to demonstrate practical implementation of:

• Data analytics dashboards  
• API integration  
• Data visualization  
• Real-world analytics applications
""")
st.divider()
st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/4413/4413567.png" width="45">
            <h3 style="margin:0;">Technologies Used</h3>
        </div>
        """, unsafe_allow_html=True)


st.markdown("""
**Frontend**
- Streamlit
- HTML/CSS for custom styling

**Backend**
- Python
            
**Database**
- SQL
- Supabase
- Postgres
            
**Data Processing**
- Pandas
- NumPy

**Visualization**
- Plotly

**API**
- YouTube Data API v3
""")
st.divider()

st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/19037/19037117.png" width="45">
            <h3 style="margin:0;">System Architecture</h3>
        </div>
        """, unsafe_allow_html=True)


st.markdown("""
User Input → Streamlit Interface → YouTube API  
→ Data Processing (Pandas) → Visualization (Plotly) → Insights Dashboard
""")
st.divider()

st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/17047/17047745.png" width="45">
            <h3 style="margin:0;">Key Metrics</h3>
        </div>
        """, unsafe_allow_html=True)

col1,col2,col3 = st.columns(3)

col1.metric("Modules","4")
col2.metric("Charts","10+")
col3.metric("APIs Used","1")
st.divider()
st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/13163/13163215.png" width="45">
            <h4 style="margin:0;">Future Enhancements</h4>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
• AI based content strategy recommendations  
• Channel growth prediction  
• Revenue estimation tools  
• Trending topic discovery  
• Multi-channel analytics
""")
st.divider()
# 👤 Founder Section
st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/6110/6110185.png" width="45">
            <h3 style="margin:0;">Meet the Creator</h3>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
### _Parth Pandurang Bulbule_  

Engineering Student | Information Technology  
@Mahatma Gandhi Mission's College of Engineering, Nanded


I am passionate about building intelligent systems that solve real-world problems.
With a strong interest in analytics, AI, and software development, I focus on 
creating structured, efficient, and scalable solutions.

InsightTube was built as a step toward mastering data systems, API integrations, 
and analytics architecture — combining engineering logic with digital creativity.

My long-term vision is to build impactful technology products that leverage 
data and artificial intelligence for smarter decision-making.
""")

st.markdown("---")

st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/1017/1017466.png" width="45">
            <h3 style="margin:0;">Connect With Me</h3>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div style="display: flex; gap: 25px; margin-top: 10px;">

<a href="https://www.linkedin.com/in/parth-bulbule/" target="_blank">
    <button style="
        background-color: #0A66C2;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        cursor: pointer;">
        🔗 LinkedIn
    </button>
</a>

<a href="https://www.instagram.com/parthbo.7/?utm_source=qr&r=nametag" target="_blank">
    <button style="
        background-color: #E1306C;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        cursor: pointer;">
        📸 Instagram
    </button>
</a>

</div>
""", unsafe_allow_html=True)
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
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="https://cdn-icons-png.flaticon.com/128/7119/7119415.png" width="45">
            <h3 style="margin:0;"> Ideas & Feedback</h3>
        </div>
        """, unsafe_allow_html=True)

name = st.text_input("Name")
email = st.text_input("Email")
message = st.text_area("Your Idea / Feedback")

if st.button("Submit"):

    data = {
        "name": name,
        "email": email,
        "message": message
    }

    supabase.table("ideas_feedback").insert(data).execute()

    st.success("Thanks! Your feedback was submitted.")
    st.balloons()