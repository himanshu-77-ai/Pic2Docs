"""
supabase_client.py — Supabase Connection
"""
import os
import streamlit as st

@st.cache_resource
def get_supabase():
    try:
        from supabase import create_client, Client
        url  = os.environ.get("SUPABASE_URL", "")
        key  = os.environ.get("SUPABASE_ANON_KEY", "")
        if not url or not key:
            return None
        # Works with both old sb_publishable_ and new eyJ formats
        return create_client(url, key)
    except Exception as e:
        return None
