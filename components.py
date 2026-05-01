import streamlit as st

def apply_tab_styling():
    st.markdown("""
    <style>
    /* Modern Streamlit Tabs */
    button[role="tab"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 12px 28px !important;
        border-radius: 50px !important;
        background-color: #1e293b !important;
        color: #94A3B8 !important;
        border: 1px solid #334155 !important;
        transition: all 0.3s ease !important;
        margin-right: 12px !important;
    }
    button[role="tab"]:hover {
        background-color: #334155 !important;
        color: #F8FAFC !important;
        transform: translateY(-2px);
    }
    button[role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6 0%, #6366F1 100%) !important;
        color: white !important;
        border: 1px solid transparent !important;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4) !important;
    }
    [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: none !important;
        padding-bottom: 15px !important;
        margin-bottom: 10px !important;
    }
    [data-baseweb="tab-panel"] {
        padding-top: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)
