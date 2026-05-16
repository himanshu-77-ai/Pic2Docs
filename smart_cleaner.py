"""
smart_cleaner.py — Intelligent OCR Post-Processing + NLP Tools
────────────────────────────────────────────────────────────────
Features:
  1. OCR Error Auto-Fixer   — spaced letters, punctuation, number confusion
  2. Extractive Summarizer  — top sentences by keyword density (no API needed)
  3. Keyword Extractor      — TF-based top keywords, no stopwords
  4. Reading Time Estimator — based on word count
  5. Text Statistics        — grade level (Flesch-Kincaid), sentence stats
  6. Auto Language Detector — detect script from unicode ranges
"""
from __future__ import annotations
import re, math, logging

logger = logging.getLogger("pic2docs.cleaner")
RTL_LANG_CODES = {"ar", "ur", "fa"}

_STOPWORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with","is","are",
    "was","were","be","been","have","has","had","do","does","did","will","would","could",
    "should","this","that","these","those","it","its","i","we","you","he","she","they",
    "me","him","her","us","them","my","your","his","our","their","from","by","as","if",
    "not","no","all","any","some","one","also","just","so","up","out","about","into",
    "more","other","such","how","what","when","where","who","which","new","then","than",
}


# ── OCR Fixing ────────────────────────────────────────────────────────────────

def _fix_spaced_letters(text: str) -> str:
    return re.sub(r"(?<!\w)((?:[A-Za-z] ){3,}[A-Za-z])(?!\w)",
                  lambda m: m.group(0).replace(" ", ""), text)

def _fix_punctuation_spacing(text: str) -> str:
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    text = re.sub(r"([\(\[{])\s+", r"\1", text)
    text = re.sub(r"\s+([\)\]}])", r"\1", text)
    return text

def _fix_number_ocr(text: str) -> str:
    text = re.sub(r"(?<=\d)O(?=\d)", "0", text)
    text = re.sub(r"(?<=\d)l(?=\d)", "1", text)
    text = re.sub(r"(?<=\d)I(?=\d)", "1", text)
    return text

def _collapse_blanks(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)

def _dedup_lines(text: str) -> str:
    out, prev = [], None
    for line in text.split("\n"):
        s = line.strip()
        if s and s == prev:
            continue
        out.append(line)
        if s:
            prev = s
    return "\n".join(out)

def _remove_garbage(text: str) -> str:
    out = []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            out.append(line); continue
        has_alpha = bool(re.search(
            r"[A-Za-z\u0900-\u097F\u0600-\u06FF\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7AF]", s))
        if not has_alpha and len(s) <= 2:
            continue
        out.append(line)
    return "\n".join(out)

def _fix_capitalisation(text: str) -> str:
    text = re.sub(r"([.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)
    return text[0].upper() + text[1:] if text and text[0].islower() else text

def clean_ocr_text(text: str, lang_code: str = "en", aggressive: bool = False) -> str:
    """Full OCR cleaning pipeline. Returns cleaned text."""
    if not text or not text.strip():
        return text
    is_rtl = lang_code in RTL_LANG_CODES
    text = _fix_number_ocr(text)
    text = _collapse_blanks(text)
    text = _dedup_lines(text)
    text = _remove_garbage(text)
    if not is_rtl:
        text = _fix_spaced_letters(text)
        text = _fix_punctuation_spacing(text)
        text = _fix_capitalisation(text)
    if aggressive and not is_rtl:
        # Merge very short lines into paragraphs
        lines = text.split("\n")
        out, buf = [], ""
        for line in lines:
            s = line.strip()
            if not s:
                if buf: out.append(buf.strip()); buf = ""
                out.append(""); continue
            if buf and len(buf) < 40 and not re.search(r"[.!?]\s*$", buf):
                buf += " " + s
            else:
                if buf: out.append(buf.strip())
                buf = s
        if buf: out.append(buf.strip())
        text = "\n".join(out)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" +\n", "\n", text)
    return text.strip()


# ── NLP Tools ─────────────────────────────────────────────────────────────────

def extract_keywords(text: str, top_n: int = 12) -> list[str]:
    """Return [(keyword, count)] sorted by frequency. Filters stopwords."""
    words = re.findall(r"\b[A-Za-z]{3,}\b", text.lower())
    freq: dict[str, int] = {}
    for w in words:
        if w not in _STOPWORDS:
            freq[w] = freq.get(w, 0) + 1
    return [w.capitalize() for w, _ in
            sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]]


def summarize_text(text: str, max_sentences: int = 4) -> str:
    """
    Extractive summary — picks highest-scoring sentences by keyword density.
    No external API, fully offline.
    """
    if not text.strip():
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    if len(sentences) <= max_sentences:
        return text.strip()
    kw_set = {w.lower() for w in extract_keywords(text, top_n=20)}
    def score(s: str) -> float:
        words = re.findall(r"\b[A-Za-z]{3,}\b", s.lower())
        return sum(1 for w in words if w in kw_set) / max(len(words), 1)
    scored = sorted(enumerate(sentences), key=lambda x: score(x[1]), reverse=True)
    top = sorted(scored[:max_sentences], key=lambda x: x[0])
    return " ".join(s for _, s in top)


def reading_time(text: str) -> str:
    """Estimate reading time (avg 200 wpm)."""
    words = len(text.split())
    mins = words / 200
    if mins < 1:
        return f"~{max(int(mins * 60), 5)} sec read"
    return f"~{math.ceil(mins)} min read"


def text_statistics(text: str) -> dict:
    """
    Return rich statistics about the text:
    word_count, sentence_count, avg_sentence_length,
    flesch_kincaid_grade (readability), paragraph_count, unique_words
    """
    words = re.findall(r"\b\w+\b", text)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
    syllables = sum(_count_syllables(w) for w in words)
    n_words = max(len(words), 1)
    n_sents = max(len(sentences), 1)
    # Flesch-Kincaid Grade Level
    fk_grade = 0.39 * (n_words / n_sents) + 11.8 * (syllables / n_words) - 15.59
    fk_grade = round(max(0, min(fk_grade, 18)), 1)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    unique = len({w.lower() for w in words})
    return {
        "word_count":          n_words,
        "sentence_count":      n_sents,
        "paragraph_count":     len(paragraphs),
        "unique_words":        unique,
        "avg_sentence_length": round(n_words / n_sents, 1),
        "flesch_kincaid_grade": fk_grade,
        "reading_time":        reading_time(text),
        "character_count":     len(text),
    }


def _count_syllables(word: str) -> int:
    """Simple English syllable counter."""
    word = word.lower().strip(".,!?;:")
    if not word:
        return 0
    count = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def detect_script(text: str) -> str:
    """
    Auto-detect dominant script in text from unicode ranges.
    Returns a human-readable script name.
    """
    sample = text[:500]
    ranges = {
        "Arabic/Urdu":     (r"[\u0600-\u06FF]", 0),
        "Devanagari":      (r"[\u0900-\u097F]", 0),
        "Bengali":         (r"[\u0980-\u09FF]", 0),
        "Chinese/Japanese":(r"[\u4E00-\u9FFF\u3040-\u30FF]", 0),
        "Korean":          (r"[\uAC00-\uD7AF]", 0),
        "Cyrillic":        (r"[\u0400-\u04FF]", 0),
        "Thai":            (r"[\u0E00-\u0E7F]", 0),
        "Greek":           (r"[\u0370-\u03FF]", 0),
        "Tamil":           (r"[\u0B80-\u0BFF]", 0),
        "Telugu":          (r"[\u0C00-\u0C7F]", 0),
        "Gujarati":        (r"[\u0A80-\u0AFF]", 0),
        "Latin":           (r"[A-Za-z]", 0),
    }
    counts = {name: len(re.findall(pattern, sample)) for name, (pattern, _) in ranges.items()}
    dominant = max(counts, key=counts.get)
    return dominant if counts[dominant] > 3 else "Unknown"
