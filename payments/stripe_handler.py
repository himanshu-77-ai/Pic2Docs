"""
stripe_handler.py — Stripe Payment Integration
"""
from __future__ import annotations
import os
import streamlit as st

PLANS = {
    "basic": {
        "name":         "Basic",
        "price_usd":    5.00,
        "images":       100,
        "stripe_price": os.environ.get("STRIPE_BASIC_PRICE_ID", ""),
    },
    "pro": {
        "name":         "Pro",
        "price_usd":    15.00,
        "images":       "Unlimited",
        "stripe_price": os.environ.get("STRIPE_PRO_PRICE_ID", ""),
    }
}


def create_checkout_session(plan: str, user_email: str, user_id: str) -> str | None:
    try:
        import stripe
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=user_email,
            line_items=[{"price": PLANS[plan]["stripe_price"], "quantity": 1}],
            success_url=f"{os.environ.get('APP_URL','https://pic2docs-2.onrender.com')}?payment=success",
            cancel_url=f"{os.environ.get('APP_URL','https://pic2docs-2.onrender.com')}?payment=cancelled",
            metadata={"user_id": user_id, "plan": plan},
        )
        return session.url
    except Exception as e:
        st.error(f"Stripe error: {e}")
        return None
