"""
translator.py — Translation Module
Chunked translation with retry logic via deep-translator.
"""
from __future__ import annotations
import logging, time
from typing import Optional
from deep_translator import GoogleTranslator

logger = logging.getLogger("pic2docs.translator")
_CHUNK_LIMIT = 4800

# World top 30 translation target languages
TRANSLATE_LANGUAGES: dict[str, str] = {
    "English":            "en",
    "Mandarin Chinese":   "zh-CN",
    "Hindi":              "hi",
    "Spanish":            "es",
    "Arabic":             "ar",
    "Bengali":            "bn",
    "Portuguese":         "pt",
    "Russian":            "ru",
    "Urdu":               "ur",
    "Japanese":           "ja",
    "German":             "de",
    "French":             "fr",
    "Vietnamese":         "vi",
    "Korean":             "ko",
    "Turkish":            "tr",
    "Indonesian":         "id",
    "Thai":               "th",
    "Persian (Farsi)":    "fa",
    "Marathi":            "mr",
    "Tamil":              "ta",
    "Telugu":             "te",
    "Gujarati":           "gu",
    "Italian":            "it",
    "Polish":             "pl",
    "Dutch":              "nl",
    "Ukrainian":          "uk",
    "Malay":              "ms",
    "Swahili":            "sw",
    "Filipino (Tagalog)": "tl",
    "Greek":              "el",
}

def _chunk_text(text: str, chunk_size: int = _CHUNK_LIMIT) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks, current, current_len = [], [], 0
    for paragraph in text.split("\n"):
        para_len = len(paragraph) + 1
        if current_len + para_len > chunk_size and current:
            chunks.append("\n".join(current)); current = []; current_len = 0
        if para_len > chunk_size:
            for sentence in paragraph.split(". "):
                if current_len + len(sentence) > chunk_size and current:
                    chunks.append(" ".join(current)); current = []; current_len = 0
                current.append(sentence); current_len += len(sentence) + 1
        else:
            current.append(paragraph); current_len += para_len
    if current: chunks.append("\n".join(current))
    return chunks

def translate_text(text: str, target_lang_code: str, source_lang: str = "auto",
                   max_retries: int = 3) -> tuple[str, Optional[str]]:
    if not text or not text.strip():
        return "", "No text to translate."
    if target_lang_code == source_lang:
        return text, None
    chunks = _chunk_text(text)
    translated_chunks = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            translated_chunks.append(chunk); continue
        for attempt in range(1, max_retries + 1):
            try:
                result = GoogleTranslator(source=source_lang, target=target_lang_code).translate(chunk)
                translated_chunks.append(result or chunk); break
            except Exception as exc:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                else:
                    return "", f"Translation failed: {exc}. Check your internet connection."
    return "\n".join(translated_chunks), None
