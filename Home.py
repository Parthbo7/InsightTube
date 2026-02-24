import streamlit as st

st.set_page_config(page_title="InsightTube", layout="wide")

st.title("📊 InsightTube")
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
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Channel Analysis", use_container_width=True):
        st.switch_page("pages/1_Channel_Analysis.py")

with col2:
    if st.button("⚔️ Compare Channels", use_container_width=True):
        st.switch_page("pages/2_Channel_Compare.py")

with col3:
    if st.button("🌍 About Us", use_container_width=True):
        st.switch_page("pages/3_About_Us.py")

st.divider()




# -------------------- Info Section --------------------
st.markdown("""
### 🚀 What You Can Do

Welcome to **InsightTube**, your smart YouTube analytics companion.

Use this platform to:

- 📊 Analyze detailed channel performance  
- 📈 View engagement metrics & growth insights  
- ⚔️ Compare two YouTube channels side-by-side  
- 🎯 Make data-driven content decisions  

---

### 💡 Why InsightTube?

InsightTube helps creators and analysts:

✔ Understand audience engagement  
✔ Track performance trends  
✔ Compare competitive channels  
✔ Extract meaningful analytics instantly  


**Use the sidebar to navigate through features.**
""")

st.divider()

st.caption("© 2026 InsightTube | Built with Streamlit 💙 | pbo7  ")


