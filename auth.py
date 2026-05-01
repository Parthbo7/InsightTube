from supabase import create_client
import streamlit as st

try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
except:
    import os
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

try:
    supabase = create_client(supabase_url, supabase_key)
except Exception as e:
    print(f"Failed to initialize Supabase client: {e}")
    supabase = None


def login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return res
    except:
        return None


def signup(email, password):
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return res
    except:
        return None