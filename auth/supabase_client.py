"""
supabase_client.py — Supabase Connection
"""
import os
import streamlit as st

@st.cache_resource
def get_supabase():
    from supabase import create_client
    url  = os.environ.get("SUPABASE_URL", "")
    key  = os.environ.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        return None
    return create_client(url, key)
