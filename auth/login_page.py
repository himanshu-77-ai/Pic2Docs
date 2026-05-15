"""
login_page.py — Beautiful Login / Signup UI
"""
import streamlit as st
from auth.auth_manager import login, signup


def render_login_page():
    st.markdown("""
    <style>
    .login-wrap{max-width:420px;margin:2rem auto;}
    .login-logo{text-align:center;margin-bottom:1.5rem;}
    .login-logo h1{font-size:2rem;font-weight:700;
        background:linear-gradient(135deg,#6C63FF,#8B83FF);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .plan-box{background:rgba(108,99,255,0.08);border:1px solid rgba(108,99,255,0.2);
        border-radius:10px;padding:1rem;font-size:0.82rem;color:#8888A8;margin-top:1rem;}
    .plan-box b{color:#6C63FF;}
    </style>
    <div class="login-wrap">
        <div class="login-logo">
            <div style="font-size:3rem;">📄</div>
            <h1>Pic2Docs</h1>
            <p style="color:#8888A8;font-size:0.9rem;margin-top:-0.5rem;">
                AI-Powered Image to Text Converter
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "✨ Sign Up"])

        with tab1:
            email    = st.text_input("Email", key="li_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="li_pass", placeholder="••••••••")
            if st.button("Login →", type="primary", use_container_width=True, key="btn_li"):
                if not email or not password:
                    st.error("Please fill all fields.")
                else:
                    with st.spinner("Logging in..."):
                        ok, msg = login(email, password)
                    if ok:
                        st.success("Welcome back! ✅")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        with tab2:
            name  = st.text_input("Full Name", key="su_name", placeholder="Your Name")
            email2= st.text_input("Email", key="su_email", placeholder="you@example.com")
            pass1 = st.text_input("Password", type="password", key="su_p1", placeholder="Min 6 characters")
            pass2 = st.text_input("Confirm Password", type="password", key="su_p2", placeholder="Repeat password")

            if st.button("Create Free Account →", type="primary", use_container_width=True, key="btn_su"):
                if not all([name, email2, pass1, pass2]):
                    st.error("Please fill all fields.")
                elif pass1 != pass2:
                    st.error("Passwords don't match.")
                elif len(pass1) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating account..."):
                        ok, msg = signup(email2, pass1, name)
                    if ok:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")

            st.markdown("""
            <div class="plan-box">
                <b>Free Plan includes:</b><br>
                ✅ 10 images/month free<br>
                ✅ Handwriting + printed text<br>
                ✅ 24 languages OCR<br>
                ✅ PDF, Word, Excel export<br>
                ✅ Translation to 14 languages
            </div>
            """, unsafe_allow_html=True)
