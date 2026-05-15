"""
ocr_engine.py — Google Cloud Vision OCR Pipeline
──────────────────────────────────────────────────
Uses Google Vision API for high accuracy OCR
- Handwritten text: 95%+ accuracy
- Printed text: 99%+ accuracy
- Supports all major languages
- Lightweight: no heavy ML models needed
"""
from __future__ import annotations
import io
import os
import base64
import logging
import requests
from typing import NamedTuple
from PIL import Image, ImageEnhance, ImageOps

logger = logging.getLogger("pic2docs.ocr")

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_DIMENSION   = 3000

LANGUAGE_MAP: dict[str, str] = {
    "English":               "en",
    "Hindi":                 "hi",
    "Arabic":                "ar",
    "Bengali":               "bn",
    "Portuguese":            "pt",
    "Russian":               "ru",
    "Urdu":                  "ur",
    "German":                "de",
    "French":                "fr",
    "Vietnamese":            "vi",
    "Korean":                "ko",
    "Turkish":               "tr",
    "Indonesian":            "id",
    "Thai":                  "th",
    "Marathi":               "mr",
    "Tamil":                 "ta",
    "Telugu":                "te",
    "Gujarati":              "gu",
    "Italian":               "it",
    "Spanish":               "es",
    "Chinese Simplified":    "zh-CN",
    "Chinese Traditional":   "zh-TW",
    "Japanese":              "ja",
    "Persian (Farsi)":       "fa",
}


class OCRResult(NamedTuple):
    text:        str
    confidence:  float
    block_count: int
    language:    str
    error:       str | None = None


def _preprocess(img: Image.Image) -> bytes:
    """Resize and optimize image for API."""
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > MAX_DIMENSION:
        scale = MAX_DIMENSION / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    # Enhance
    img = ImageOps.autocontrast(img.convert("L"), cutoff=1).convert("RGB")
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def run_ocr(file_bytes: bytes, filename: str, lang_code: str) -> OCRResult:
    """Run Google Vision OCR."""

    api_key = os.environ.get("GOOGLE_VISION_API_KEY", "")
    if not api_key:
        return OCRResult("", 0.0, 0, lang_code,
            "Google Vision API key not found. Please set GOOGLE_VISION_API_KEY in Render environment.")

    if len(file_bytes) > MAX_IMAGE_BYTES:
        return OCRResult("", 0.0, 0, lang_code,
            f"File too large. Max {MAX_IMAGE_BYTES//1_048_576}MB.")
    if len(file_bytes) == 0:
        return OCRResult("", 0.0, 0, lang_code, "Empty file.")

    # Preprocess
    try:
        img = Image.open(io.BytesIO(file_bytes))
        processed_bytes = _preprocess(img)
    except Exception as exc:
        return OCRResult("", 0.0, 0, lang_code, f"Image error: {exc}")

    # Encode to base64
    img_b64 = base64.b64encode(processed_bytes).decode("utf-8")

    # Call Google Vision API
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    payload = {
        "requests": [{
            "image": {"content": img_b64},
            "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
            "imageContext": {
                "languageHints": [lang_code]
            }
        }]
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        return OCRResult("", 0.0, 0, lang_code, "API timeout. Please try again.")
    except Exception as exc:
        return OCRResult("", 0.0, 0, lang_code, f"API error: {exc}")

    # Parse response
    try:
        response = data["responses"][0]

        if "error" in response:
            return OCRResult("", 0.0, 0, lang_code,
                f"Vision API error: {response['error']['message']}")

        if "fullTextAnnotation" not in response:
            return OCRResult(
                "No text detected. Try a clearer image.",
                0.0, 0, lang_code)

        full_text = response["fullTextAnnotation"]["text"].strip()

        # Calculate confidence from word confidences
        pages = response["fullTextAnnotation"].get("pages", [])
        confidences = []
        block_count = 0
        for page in pages:
            for block in page.get("blocks", []):
                block_count += 1
                conf = block.get("confidence", 0.0)
                if conf > 0:
                    confidences.append(conf)

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.85

        return OCRResult(
            text=full_text,
            confidence=avg_conf,
            block_count=block_count,
            language=lang_code,
        )

    except Exception as exc:
        logger.exception("Response parse error: %s", exc)
        return OCRResult("", 0.0, 0, lang_code, f"Response error: {exc}")
