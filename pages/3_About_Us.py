import streamlit as st
st.set_page_config(layout="wide")
st.title("👨‍💻 About Us")
st.divider()
st.set_page_config(
    page_title="InsightTube",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    st.markdown("## 📊 InsightTube")
    st.divider()

    st.page_link("Home.py", label="🏠 Home")
    st.page_link("pages/1_Channel_Analysis.py", label="📊 Channel Analysis")
    st.page_link("pages/2_Channel_Compare.py", label="⚔️ Channel Compare")
    st.page_link("pages/3_About_Us.py", label="🌍 About Us")


st.set_page_config(page_title="About Us", page_icon="🚀")

st.title("🚀 About InsightTube")

st.markdown("""
## Who We Are  

At **InsightTube**, we believe data should do more than just sit in a dashboard —  
it should tell a story.

We are building a powerful yet simple platform that helps creators, analysts, 
and curious minds understand YouTube performance deeply.  

From channel insights to video analytics and engagement metrics,  
our goal is to transform raw data into meaningful decisions.
""")
st.divider()

# 👤 Founder Section
st.header("👤 Meet the Creator")
st.markdown("""
### Parth Pandurang Bulbule  

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
st.markdown("### 🌐 Connect With Me")

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

st.caption("© 2026 InsightTube | Built with Streamlit 💙")
