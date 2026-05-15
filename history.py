"""
history.py — Session OCR History Manager
─────────────────────────────────────────
Stores OCR results in Streamlit session state.
- Save, load, delete past OCR results in same session
- Export full history as combined TXT or JSON
- No disk/DB needed — pure in-memory
"""
from __future__ import annotations
import json
import logging
from datetime import datetime
from dataclasses import dataclass, asdict

import streamlit as st

logger = logging.getLogger("pic2docs.history")

HISTORY_KEY = "_pic2docs_history"
MAX_HISTORY = 20


@dataclass
class HistoryEntry:
    id:         str
    filename:   str
    language:   str
    text:       str
    confidence: float
    blocks:     int
    timestamp:  str

    def short_preview(self, n: int = 80) -> str:
        clean = " ".join(self.text.split())
        return clean[:n] + ("…" if len(clean) > n else "")


def _get_history() -> list[HistoryEntry]:
    if HISTORY_KEY not in st.session_state:
        st.session_state[HISTORY_KEY] = []
    return st.session_state[HISTORY_KEY]


def save_to_history(filename: str, language: str, text: str,
                    confidence: float, blocks: int) -> HistoryEntry:
    history = _get_history()
    entry = HistoryEntry(
        id=datetime.now().strftime("%Y%m%d%H%M%S%f"),
        filename=filename,
        language=language,
        text=text,
        confidence=confidence,
        blocks=blocks,
        timestamp=datetime.now().strftime("%d %b %Y, %H:%M:%S"),
    )
    history.insert(0, entry)
    if len(history) > MAX_HISTORY:
        history.pop()
    logger.info("Saved to history: %s (%d entries total)", filename, len(history))
    return entry


def get_history() -> list[HistoryEntry]:
    return _get_history()


def delete_entry(entry_id: str) -> None:
    history = _get_history()
    st.session_state[HISTORY_KEY] = [e for e in history if e.id != entry_id]


def clear_history() -> None:
    st.session_state[HISTORY_KEY] = []


def export_history_txt() -> bytes:
    history = _get_history()
    parts = []
    for i, e in enumerate(history, 1):
        parts.append(
            f"{'='*60}\n"
            f"Entry {i}: {e.filename}\n"
            f"Time: {e.timestamp} | Lang: {e.language} | "
            f"Confidence: {int(e.confidence*100)}% | Blocks: {e.blocks}\n"
            f"{'─'*60}\n{e.text}\n"
        )
    return "\n".join(parts).encode("utf-8")


def export_history_json() -> bytes:
    history = _get_history()
    return json.dumps([asdict(e) for e in history],
                      ensure_ascii=False, indent=2).encode("utf-8")
