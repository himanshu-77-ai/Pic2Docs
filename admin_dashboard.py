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

    try:
        # Try to get users from auth
        users = sb.table("profiles").select("*").execute().data or []
        payments = sb.table("payments").select("*").eq("status","success").execute().data or []

        total_revenue = sum(p.get("amount", 0) for p in payments)
        free_users    = sum(1 for u in users if u.get("plan") == "free")
        paid_users    = sum(1 for u in users if u.get("plan") in ("basic","pro"))

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total Users",   len(users))
        c2.metric("Paid Users",    paid_users)
        c3.metric("Free Users",    free_users)
        c4.metric("Total Revenue", f"${total_revenue:.2f}")

        st.markdown("---")

        if users:
            import pandas as pd
            st.markdown("### 👥 All Users")
            df = pd.DataFrame(users)
            cols = [c for c in ["email","plan","images_used","images_limit","created_at"] if c in df.columns]
            st.dataframe(df[cols] if cols else df, use_container_width=True)

        if payments:
            import pandas as pd
            st.markdown("### 💰 Recent Payments")
            df2 = pd.DataFrame(payments)
            cols2 = [c for c in ["amount","currency","gateway","status","created_at"] if c in df2.columns]
            st.dataframe(df2[cols2] if cols2 else df2, use_container_width=True)

        if not users and not payments:
            st.info("No data yet — users will appear here after signup!")

    except Exception as e:
        st.warning(f"⚠️ Database tables not set up yet. Please run the SQL schema in Supabase.")
        st.markdown("""
        **Steps to fix:**
        1. Go to Supabase → SQL Editor
        2. Run the `database_schema.sql` file
        3. Refresh this page
        """)
        with st.expander("Error details"):
            st.code(str(e))
