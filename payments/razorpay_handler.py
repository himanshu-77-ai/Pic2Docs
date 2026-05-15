"""
razorpay_handler.py — Razorpay Payment Integration (India)
"""
from __future__ import annotations
import os
import hmac
import hashlib
import streamlit as st

PLANS_INR = {
    "basic": {
        "name":    "Basic",
        "price":   399,
        "images":  100,
        "plan_id": os.environ.get("RAZORPAY_BASIC_PLAN_ID", ""),
    },
    "pro": {
        "name":    "Pro",
        "price":   1199,
        "images":  "Unlimited",
        "plan_id": os.environ.get("RAZORPAY_PRO_PLAN_ID", ""),
    }
}


def create_subscription(plan: str, user_email: str) -> dict | None:
    try:
        import razorpay
        client = razorpay.Client(auth=(
            os.environ.get("RAZORPAY_KEY_ID", ""),
            os.environ.get("RAZORPAY_KEY_SECRET", "")
        ))
        return client.subscription.create({
            "plan_id":         PLANS_INR[plan]["plan_id"],
            "total_count":     12,
            "customer_notify": 1,
            "notes":           {"email": user_email},
        })
    except Exception as e:
        st.error(f"Razorpay error: {e}")
        return None


def verify_payment(pay_id: str, sub_id: str, signature: str) -> bool:
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET", "")
    msg = f"{pay_id}|{sub_id}"
    expected = hmac.new(key_secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
