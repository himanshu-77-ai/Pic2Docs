"""
auth_manager.py — Login / Signup / Session
"""
from __future__ import annotations
import streamlit as st
from auth.supabase_client import get_supabase


def get_current_user():
    """Get logged in user from session."""
    return st.session_state.get("user", None)


def is_logged_in() -> bool:
    return st.session_state.get("user") is not None


def login(email: str, password: str) -> tuple[bool, str]:
    """Login with email/password."""
    sb = get_supabase()
    if not sb:
        return False, "Database not connected."
    try:
        resp = sb.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state["user"]         = resp.user
        st.session_state["access_token"] = resp.session.access_token
        return True, "Login successful!"
    except Exception as e:
        return False, str(e).replace("AuthApiError: ", "")


def signup(email: str, password: str, full_name: str) -> tuple[bool, str]:
    """Register new user."""
    sb = get_supabase()
    if not sb:
        return False, "Database not connected."
    try:
        resp = sb.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": full_name}}
        })
        if resp.user:
            return True, "Account created! Please check your email to verify."
        return False, "Signup failed. Try again."
    except Exception as e:
        return False, str(e).replace("AuthApiError: ", "")


def logout():
    """Logout current user."""
    sb = get_supabase()
    if sb:
        try: sb.auth.sign_out()
        except: pass
    for key in ["user", "access_token", "profile"]:
        st.session_state.pop(key, None)


def get_profile() -> dict | None:
    """Get user profile from database."""
    if not is_logged_in():
        return None
    if "profile" in st.session_state:
        return st.session_state["profile"]
    sb = get_supabase()
    if not sb:
        return None
    try:
        user_id = st.session_state["user"].id
        resp = sb.table("profiles").select("*").eq("id", user_id).single().execute()
        st.session_state["profile"] = resp.data
        return resp.data
    except:
        return None


def check_usage_limit() -> tuple[bool, int, int]:
    """
    Check if user can do OCR.
    Returns: (can_use, used, limit)
    """
    profile = get_profile()
    if not profile:
        return False, 0, 0
    used  = profile.get("images_used", 0)
    limit = profile.get("images_limit", 10)
    return used < limit, used, limit


def increment_usage():
    """Increment OCR usage count."""
    sb = get_supabase()
    if not sb or not is_logged_in():
        return
    try:
        user_id = st.session_state["user"].id
        profile = get_profile()
        new_count = (profile.get("images_used", 0) or 0) + 1
        sb.table("profiles").update({"images_used": new_count}).eq("id", user_id).execute()
        if "profile" in st.session_state:
            st.session_state["profile"]["images_used"] = new_count
    except Exception as e:
        pass


def save_ocr_history(filename: str, language: str, word_count: int, confidence: float):
    """Save OCR result to history."""
    sb = get_supabase()
    if not sb or not is_logged_in():
        return
    try:
        user_id = st.session_state["user"].id
        sb.table("ocr_history").insert({
            "user_id":    user_id,
            "filename":   filename,
            "language":   language,
            "word_count": word_count,
            "confidence": round(confidence, 3),
        }).execute()
    except:
        pass
