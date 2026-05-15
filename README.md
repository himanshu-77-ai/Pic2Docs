# 📄 Pic2Docs v3.0 — Image to Text Converter

AI-powered OCR web app. Upload any image (handwritten notes, printed docs, receipts, scanned pages), extract text instantly, edit, export, translate — and more.

---

## ✨ What's New in v3.0

| Feature | Details |
|---|---|
| **5 Tabs** | OCR · Image Tools · Batch OCR · History · Summarize |
| **Smart Auto-Fix** | Fixes OCR errors, spacing, punctuation automatically |
| **Image Editor** | Crop, rotate, brightness, contrast, denoise before OCR |
| **Batch OCR** | Upload 20+ images, process all at once, combined export |
| **Session History** | Save/restore/export past OCR results |
| **AI Summarize** | Keyword extraction + extractive summarization + reading stats |
| **24 OCR Languages** | All top world languages (see table below) |
| **6 UI Languages** | English, Hindi, Urdu, French, Spanish, Arabic (RTL supported) |
| **5 Export Formats** | TXT, PDF, Word, Excel, Notebook PNG |
| **14 Translation Languages** | via Google Translate |

---

## 🌍 Supported OCR Languages

| Language | | Language | | Language |
|---|---|---|---|---|
| English | | Mandarin Chinese | | Hindi |
| Spanish | | Arabic | | Bengali |
| Portuguese | | Russian | | Urdu |
| Japanese | | German | | French |
| Vietnamese | | Korean | | Turkish |
| Indonesian | | Thai | | Persian (Farsi) |
| Marathi | | Tamil | | Telugu |
| Gujarati | | Italian | | Chinese (Traditional) |

---

## 📁 Project Structure

```
Pic2Docs/
│
├── app.py            ← Main app — 5 tabs, multi-language UI
├── ocr_engine.py     ← Image validation + EasyOCR pipeline
├── exporter.py       ← TXT / PDF / Word / Excel / PNG export
├── translator.py     ← Google Translate with retry logic
├── smart_cleaner.py  ← OCR auto-fix + keywords + summarizer
├── history.py        ← Session history manager
├── image_tools.py    ← Crop / rotate / enhance tools
├── batch_ocr.py      ← Multi-image batch processor
├── ui_strings.py     ← UI text in 6 languages
├── requirements.txt  ← Python dependencies
├── Dockerfile        ← Docker production config
├── DejaVuSans.ttf    ← ⚠️ Download separately (see below)
│
└── .streamlit/
    └── config.toml   ← Dark theme + server settings
```

> ⚠️ **`DejaVuSans.ttf` required** for PDF & Notebook PNG export.  
> Download free: https://dejavu-fonts.github.io/ → place in project root.

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
# Open http://localhost:8501
```

### Docker
```bash
docker build -t pic2docs .
docker run -p 8501:8501 pic2docs
```

---

## 🛠 Tech Stack

Streamlit · EasyOCR · Pillow · OpenCV · fpdf2 · python-docx · pandas · deep-translator
