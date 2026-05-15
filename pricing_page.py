"""
pricing_page.py — Pricing & Upgrade UI
"""
import streamlit as st
import os
from payments.stripe_handler import PLANS, create_checkout_session
from payments.razorpay_handler import PLANS_INR
from auth.auth_manager import get_current_user, get_profile


def render_pricing_page():
    profile = get_profile()
    current_plan = profile.get("plan", "free") if profile else "free"
    used         = profile.get("images_used", 0) if profile else 0
    limit        = profile.get("images_limit", 10) if profile else 10

    st.markdown("""
    <div style="text-align:center;margin-bottom:2rem;">
        <h2 style="font-weight:700;">Choose Your Plan</h2>
        <p style="color:#8888A8;">Upgrade to process more images every month</p>
    </div>
    """, unsafe_allow_html=True)

    # Current usage bar
    pct = int((used / limit) * 100) if limit > 0 else 0
    color = "#FF5C5C" if pct >= 90 else ("#F5A623" if pct >= 70 else "#22C87A")
    st.markdown(f"""
    <div style="background:#1A1A2E;border:1px solid rgba(108,99,255,0.25);
         border-radius:12px;padding:1rem 1.25rem;margin-bottom:1.5rem;">
        <div style="font-size:0.8rem;color:#8888A8;margin-bottom:6px;">
            Current usage this month
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
            <span style="font-weight:600;">{used} / {limit} images</span>
            <span style="color:{color};font-weight:600;">{pct}% used</span>
        </div>
        <div style="background:#0F0F1A;border-radius:100px;height:8px;">
            <div style="width:{pct}%;background:{color};height:100%;border-radius:100px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Plan cards
    c1, c2, c3 = st.columns(3)

    # Free Plan
    with c1:
        st.markdown(f"""
        <div style="background:#1A1A2E;border:1px solid {'#6C63FF' if current_plan=='free' else 'rgba(108,99,255,0.25)'};
             border-radius:14px;padding:1.5rem;text-align:center;height:320px;">
            <div style="font-size:0.7rem;font-weight:700;letter-spacing:2px;color:#8888A8;">FREE</div>
            <div style="font-size:2.5rem;font-weight:700;margin:0.5rem 0;">$0</div>
            <div style="color:#8888A8;font-size:0.85rem;margin-bottom:1rem;">per month</div>
            <hr style="border-color:rgba(108,99,255,0.2);">
            <div style="font-size:0.85rem;line-height:2;text-align:left;">
                ✅ 10 images/month<br>
                ✅ All export formats<br>
                ✅ Translation<br>
                ✅ Batch OCR<br>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if current_plan == "free":
            st.markdown('<div style="text-align:center;margin-top:8px;color:#6C63FF;font-size:0.85rem;">✓ Current Plan</div>', unsafe_allow_html=True)

    # Basic Plan
    with c2:
        st.markdown(f"""
        <div style="background:#1A1A2E;border:2px solid {'#6C63FF' if current_plan=='basic' else 'rgba(108,99,255,0.4)'};
             border-radius:14px;padding:1.5rem;text-align:center;height:320px;">
            <div style="font-size:0.7rem;font-weight:700;letter-spacing:2px;color:#6C63FF;">BASIC</div>
            <div style="font-size:2.5rem;font-weight:700;margin:0.5rem 0;">$5</div>
            <div style="color:#8888A8;font-size:0.85rem;margin-bottom:1rem;">per month</div>
            <hr style="border-color:rgba(108,99,255,0.2);">
            <div style="font-size:0.85rem;line-height:2;text-align:left;">
                ✅ 100 images/month<br>
                ✅ All export formats<br>
                ✅ Translation<br>
                ✅ Priority support<br>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if current_plan != "basic":
            col_a, col_b = st.columns(2)
            user = get_current_user()
            with col_a:
                if st.button("💳 USD", key="basic_stripe", use_container_width=True):
                    url = create_checkout_session("basic", user.email, user.id)
                    if url: st.markdown(f'<meta http-equiv="refresh" content="0;url={url}">', unsafe_allow_html=True)
            with col_b:
                if st.button("₹ INR", key="basic_rzp", use_container_width=True):
                    st.info(f"₹{PLANS_INR['basic']['price']}/month — Razorpay coming soon!")
        else:
            st.markdown('<div style="text-align:center;margin-top:8px;color:#6C63FF;font-size:0.85rem;">✓ Current Plan</div>', unsafe_allow_html=True)

    # Pro Plan
    with c3:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(108,99,255,0.2),rgba(108,99,255,0.05));
             border:2px solid #6C63FF;border-radius:14px;padding:1.5rem;text-align:center;height:320px;position:relative;">
            <div style="position:absolute;top:-12px;left:50%;transform:translateX(-50%);
                 background:#6C63FF;color:white;font-size:0.7rem;font-weight:700;
                 padding:3px 12px;border-radius:100px;">MOST POPULAR</div>
            <div style="font-size:0.7rem;font-weight:700;letter-spacing:2px;color:#6C63FF;">PRO</div>
            <div style="font-size:2.5rem;font-weight:700;margin:0.5rem 0;">$15</div>
            <div style="color:#8888A8;font-size:0.85rem;margin-bottom:1rem;">per month</div>
            <hr style="border-color:rgba(108,99,255,0.2);">
            <div style="font-size:0.85rem;line-height:2;text-align:left;">
                ✅ Unlimited images<br>
                ✅ All export formats<br>
                ✅ Translation<br>
                ✅ Priority support<br>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if current_plan != "pro":
            col_a, col_b = st.columns(2)
            user = get_current_user()
            with col_a:
                if st.button("💳 USD", key="pro_stripe", use_container_width=True):
                    url = create_checkout_session("pro", user.email, user.id)
                    if url: st.markdown(f'<meta http-equiv="refresh" content="0;url={url}">', unsafe_allow_html=True)
            with col_b:
                if st.button("₹ INR", key="pro_rzp", use_container_width=True):
                    st.info(f"₹{PLANS_INR['pro']['price']}/month — Razorpay coming soon!")
        else:
            st.markdown('<div style="text-align:center;margin-top:8px;color:#6C63FF;font-size:0.85rem;">✓ Current Plan</div>', unsafe_allow_html=True)
