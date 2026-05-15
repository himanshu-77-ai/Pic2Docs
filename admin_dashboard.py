"""
admin_dashboard.py — Admin Panel
Only accessible to admin email
"""
import os
import streamlit as st
from auth.supabase_client import get_supabase
from auth.auth_manager import get_current_user

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")


def is_admin() -> bool:
    user = get_current_user()
    if not user:
        return False
    return user.email == ADMIN_EMAIL


def render_admin_dashboard():
    if not is_admin():
        st.error("Access denied.")
        return

    sb = get_supabase()
    st.markdown("## 🛠 Admin Dashboard")

    # Stats
    try:
        users   = sb.table("profiles").select("*").execute().data
        subs    = sb.table("subscriptions").select("*").eq("status","active").execute().data
        payments= sb.table("payments").select("*").eq("status","success").execute().data

        total_revenue = sum(p.get("amount", 0) for p in payments)
        free_users    = sum(1 for u in users if u.get("plan") == "free")
        paid_users    = sum(1 for u in users if u.get("plan") in ("basic","pro"))

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total Users",    len(users))
        c2.metric("Paid Users",     paid_users)
        c3.metric("Free Users",     free_users)
        c4.metric("Total Revenue",  f"${total_revenue:.2f}")

        st.markdown("---")

        # Users table
        st.markdown("### 👥 All Users")
        if users:
            import pandas as pd
            df = pd.DataFrame(users)[["email","plan","images_used","images_limit","created_at"]]
            st.dataframe(df, use_container_width=True)

        # Recent payments
        st.markdown("### 💰 Recent Payments")
        if payments:
            df2 = pd.DataFrame(payments)[["amount","currency","gateway","status","created_at"]]
            st.dataframe(df2, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading data: {e}")
