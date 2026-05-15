"""
app.py — Pic2Docs v3.0 Production App
───────────────────────────────────────
Tabs:
  1. OCR          — Single image OCR + edit + export
  2. Image Tools  — Crop / rotate / enhance before OCR  
  3. Batch OCR    — Multiple images at once
  4. History      — Past session results
  5. Summarize    — AI keyword + summary extraction

Multi-language UI: English, Hindi, Urdu, French, Spanish, Arabic
Run:  streamlit run app.py
"""
from __future__ import annotations
import io, logging, sys
from pathlib import Path

import streamlit as st
from PIL import Image

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger("pic2docs.app")

from ocr_engine   import run_ocr, LANGUAGE_MAP, OCRResult
from exporter     import export_txt, export_pdf, export_docx, export_xlsx, export_notebook_png
from translator   import translate_text, TRANSLATE_LANGUAGES
from ui_strings   import UI_STRINGS, get_strings, is_rtl, DEFAULT_UI_LANG
from smart_cleaner import clean_ocr_text, extract_keywords, summarize_text
from history      import save_to_history, get_history, delete_entry, clear_history, export_history_txt, export_history_json
from image_tools  import apply_all, pil_to_bytes
from batch_ocr    import run_batch_ocr, combine_results_txt, batch_stats

APP_NAME    = "Pic2Docs"
APP_VERSION = "3.0.0"
MAX_MB      = 10
ALLOWED_EXT = ["png", "jpg", "jpeg", "webp", "bmp", "tiff"]

st.set_page_config(
    page_title=f"{APP_NAME} — Image to Text",
    page_icon="📄", layout="wide",
    initial_sidebar_state="expanded",
)


def _css(rtl: bool = False) -> None:
    d = "rtl" if rtl else "ltr"
    st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    :root{{--p1:#6C63FF;--p2:#8B83FF;--p3:#EBE9FF;--bg:#0F0F1A;--bg2:#16162A;--bg3:#1E1E35;
          --card:#1A1A2E;--border:rgba(108,99,255,0.25);--text:#E8E8F0;--muted:#8888A8;
          --success:#22C87A;--warn:#F5A623;--err:#FF5C5C;--radius:14px;
          --font:'Space Grotesk',sans-serif;--mono:'JetBrains Mono',monospace;}}
    html,body,[class*="css"]{{font-family:var(--font)!important;color:var(--text);direction:{d};}}
    .stApp{{background:var(--bg);}}
    #MainMenu,footer,header{{visibility:hidden;}}
    .block-container{{padding:1.5rem 2.5rem 3rem!important;max-width:1400px!important;}}
    .p2d-logo{{font-size:1.5rem;font-weight:700;background:linear-gradient(135deg,var(--p1),var(--p2));
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
    .p2d-badge{{font-size:0.68rem;font-weight:600;background:var(--p3);color:var(--p1);
                padding:2px 9px;border-radius:100px;font-family:var(--mono);}}
    .p2d-section{{font-size:0.7rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;
                  color:var(--muted);margin:1.2rem 0 0.6rem;display:flex;align-items:center;gap:10px;}}
    .p2d-section::after{{content:'';flex:1;height:1px;background:var(--border);}}
    .p2d-card{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);
               padding:1.25rem;margin-bottom:1rem;}}
    .stat-row{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:0.75rem;}}
    .stat-chip{{background:var(--bg3);border:1px solid var(--border);border-radius:100px;
                padding:3px 12px;font-size:0.76rem;font-family:var(--mono);color:var(--p2);}}
    .stat-chip span{{color:var(--muted);margin-right:4px;}}
    .kw-pill{{display:inline-block;background:rgba(108,99,255,0.15);border:1px solid var(--border);
              border-radius:100px;padding:3px 12px;font-size:0.78rem;color:var(--p2);margin:3px;}}
    .conf-bar-wrap{{background:var(--bg3);border-radius:100px;height:7px;overflow:hidden;margin-top:5px;}}
    .conf-bar-fill{{height:100%;border-radius:100px;transition:width .6s ease;}}
    .help-text{{font-size:0.77rem;color:var(--muted);margin-top:3px;line-height:1.5;}}
    .batch-row{{background:var(--bg2);border:1px solid var(--border);border-radius:10px;
                padding:0.75rem 1rem;margin-bottom:0.5rem;display:flex;align-items:center;gap:12px;}}
    .hist-row{{background:var(--bg2);border:1px solid var(--border);border-radius:10px;
               padding:0.9rem 1.1rem;margin-bottom:0.6rem;}}
    [data-testid="stFileUploader"]{{border:2px dashed var(--border)!important;
                                    border-radius:var(--radius)!important;
                                    background:var(--bg2)!important;padding:1rem!important;}}
    .stButton>button{{border-radius:10px!important;font-weight:600!important;
                      font-family:var(--font)!important;border:none!important;transition:all .18s!important;}}
    .stButton>button[kind="primary"]{{background:linear-gradient(135deg,var(--p1),#9B93FF)!important;
                                      color:#fff!important;padding:.55rem 1.8rem!important;}}
    .stButton>button[kind="primary"]:hover{{transform:translateY(-1px)!important;
                                            box-shadow:0 6px 20px rgba(108,99,255,.4)!important;}}
    .stButton>button[kind="secondary"]{{background:var(--bg3)!important;color:var(--p2)!important;
                                        border:1px solid var(--border)!important;font-size:.82rem!important;}}
    [data-testid="stDownloadButton"]>button{{background:var(--bg3)!important;color:var(--text)!important;
                                             border:1px solid var(--border)!important;border-radius:10px!important;
                                             font-family:var(--font)!important;font-weight:500!important;
                                             font-size:.82rem!important;width:100%!important;transition:all .18s!important;}}
    [data-testid="stDownloadButton"]>button:hover{{border-color:var(--p1)!important;color:var(--p1)!important;}}
    .stTextArea textarea{{font-family:var(--mono)!important;font-size:.84rem!important;
                          background:var(--bg2)!important;border-color:var(--border)!important;
                          color:var(--text)!important;border-radius:10px!important;line-height:1.65!important;}}
    .stSelectbox>div>div,.stSlider>div{{background:var(--bg2)!important;border-radius:10px!important;}}
    .stTabs [data-baseweb="tab-list"]{{background:var(--bg2);border-radius:12px;padding:4px;gap:4px;}}
    .stTabs [data-baseweb="tab"]{{border-radius:8px!important;font-weight:500!important;
                                  font-family:var(--font)!important;color:var(--muted)!important;}}
    .stTabs [aria-selected="true"]{{background:var(--p1)!important;color:#fff!important;}}
    .stProgress .st-bo{{background:var(--p1)!important;}}
    [data-testid="stImage"] img{{border-radius:var(--radius)!important;border:1px solid var(--border)!important;}}
    </style>""", unsafe_allow_html=True)


def _init():
    defaults = {
        "ocr_result": None, "edited_text": "", "translated_text": "",
        "last_filename": "", "ui_lang": DEFAULT_UI_LANG,
        "img_edited": None, "img_edit_params": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _conf_bar(conf: float, s: dict) -> str:
    pct = int(conf * 100)
    color = "#22C87A" if pct >= 80 else ("#F5A623" if pct >= 55 else "#FF5C5C")
    label = s["conf_high"] if pct >= 80 else (s["conf_med"] if pct >= 55 else s["conf_low"])
    return (f'<div style="margin-bottom:.5rem">'
            f'<span style="font-size:.77rem;color:#8888A8;">{s["conf_label"]}</span>'
            f'<span style="font-size:.77rem;font-weight:600;color:{color};">{label} ({pct}%)</span>'
            f'<div class="conf-bar-wrap"><div class="conf-bar-fill" style="width:{pct}%;background:{color};"></div></div>'
            f'</div>')


def _stats_html(result: OCRResult, s: dict) -> str:
    wc = len(result.text.split())
    lc = len([l for l in result.text.split("\n") if l.strip()])
    cc = len(result.text)
    lang = next((k for k, v in LANGUAGE_MAP.items() if v == result.language), result.language)
    return (f'<div class="stat-row">'
            f'<div class="stat-chip"><span>{s["stat_words"]}</span>{wc:,}</div>'
            f'<div class="stat-chip"><span>{s["stat_lines"]}</span>{lc:,}</div>'
            f'<div class="stat-chip"><span>{s["stat_chars"]}</span>{cc:,}</div>'
            f'<div class="stat-chip"><span>{s["stat_blocks"]}</span>{result.block_count}</div>'
            f'<div class="stat-chip"><span>{s["stat_lang"]}</span>{lang}</div>'
            f'</div>')


def _export_row(text: str, stem: str, s: dict, key_suffix: str = "") -> None:
    if not text.strip():
        st.warning(s["nothing_to_export"])
        return
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1:
        d,e = export_txt(text, stem)
        if not e: st.download_button(s["dl_txt"],  d, f"{stem}.txt",   "text/plain", key=f"dl_txt{key_suffix}",  use_container_width=True)
    with c2:
        d,e = export_pdf(text, stem)
        if not e: st.download_button(s["dl_pdf"],  d, f"{stem}.pdf",   "application/pdf", key=f"dl_pdf{key_suffix}", use_container_width=True)
    with c3:
        d,e = export_docx(text, stem)
        if not e: st.download_button(s["dl_word"], d, f"{stem}.docx",  "application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_docx{key_suffix}", use_container_width=True)
    with c4:
        d,e = export_xlsx(text, stem)
        if not e: st.download_button(s["dl_excel"],d, f"{stem}.xlsx",  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"dl_xlsx{key_suffix}", use_container_width=True)
    with c5:
        d,e = export_notebook_png(text)
        if not e: st.download_button(s["dl_notebook"],d, f"{stem}.png","image/png", key=f"dl_png{key_suffix}", use_container_width=True)


# ── TAB 1: Main OCR ───────────────────────────────────────────────────────────

def tab_ocr(s: dict) -> None:
    left, right = st.columns([1, 1.35], gap="large")

    with left:
        st.markdown(f'<div class="p2d-section">{s["upload_section"]}</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(s["upload_label"], type=ALLOWED_EXT, key="ocr_upload")

        if uploaded:
            # If user edited image in Image Tools tab, use that
            edited_bytes = st.session_state.get("img_edited")
            if edited_bytes and st.session_state.get("img_edit_source") == uploaded.name:
                display_bytes = edited_bytes
                st.info("🖊 Using your edited image from Image Tools tab.")
            else:
                uploaded.seek(0)
                display_bytes = uploaded.read()
                uploaded.seek(0)

            st.image(Image.open(io.BytesIO(display_bytes)),
                     caption=f"{uploaded.name}  ({len(display_bytes)/1024:.0f} KB)",
                     width=700)

            st.markdown(f'<div class="p2d-section">{s["settings_section"]}</div>', unsafe_allow_html=True)
            lang_name = st.selectbox(s["ocr_lang_label"], list(LANGUAGE_MAP.keys()), key="ocr_lang")
            lang_code = LANGUAGE_MAP[lang_name]
            preprocess = st.toggle(s["preprocess_label"], value=True, key="ocr_pre")

            # Smart cleaner options
            st.markdown('<div class="p2d-section">Smart Auto-Fix</div>', unsafe_allow_html=True)
            auto_clean = st.toggle("Auto-fix OCR errors after extraction", value=True, key="auto_clean",
                                   help="Fixes spacing, punctuation, duplicate lines, number confusion")
            aggressive = st.toggle("Merge broken lines into paragraphs", value=False, key="aggressive_clean",
                                   help="Joins short fragmented lines — good for scanned books")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(s["extract_btn"], type="primary", use_container_width=True, key="btn_extract"):
                if len(display_bytes) > MAX_MB * 1024 * 1024:
                    st.error(s["file_too_large"].format(max_mb=MAX_MB))
                else:
                    with st.spinner(s["extracting"]):
                        result = run_ocr(display_bytes, uploaded.name, lang_code)
                    if result.error:
                        st.error(f"❌ {result.error}")
                    else:
                        text = result.text
                        if auto_clean:
                            text = clean_ocr_text(text, lang_code, aggressive=aggressive)
                        st.session_state.update({
                            "ocr_result": result,
                            "edited_text": text,
                            "last_filename": uploaded.name,
                            "translated_text": "",
                        })
                        save_to_history(uploaded.name, lang_name, text,
                                        result.confidence, result.block_count)
                        st.success(s["extract_success"].format(
                            blocks=result.block_count, conf=int(result.confidence*100)))

    with right:
        result: OCRResult | None = st.session_state.get("ocr_result")
        if result and not result.error:
            st.markdown(_stats_html(result, s) + _conf_bar(result.confidence, s), unsafe_allow_html=True)
            st.markdown(f'<div class="p2d-section">{s["extracted_section"]}</div>', unsafe_allow_html=True)
            edited = st.text_area("", value=st.session_state["edited_text"],
                                  height=300, key="text_editor", label_visibility="collapsed")
            st.session_state["edited_text"] = edited
            ca, cb, cc = st.columns(3)
            with ca:
                if st.button(s["reset_btn"], use_container_width=True):
                    st.session_state["edited_text"] = result.text; st.rerun()
            with cb:
                if st.button("🔧 Re-clean", use_container_width=True, key="reclean"):
                    st.session_state["edited_text"] = clean_ocr_text(edited, result.language); st.rerun()
            with cc:
                if st.button(s["clear_btn"], use_container_width=True):
                    st.session_state.update({"ocr_result":None,"edited_text":"","translated_text":""}); st.rerun()

            st.markdown(f'<div class="p2d-section">{s["export_section"]}</div>', unsafe_allow_html=True)
            _export_row(edited, Path(st.session_state["last_filename"]).stem, s, "_main")

            # Translation
            st.markdown(f'<div class="p2d-section">{s["translate_section"]}</div>', unsafe_allow_html=True)
            target = st.selectbox(s["translate_to"],
                [s["translate_placeholder"]] + list(TRANSLATE_LANGUAGES.keys()),
                key="translate_target", label_visibility="collapsed")
            if target and target != s["translate_placeholder"]:
                if st.button(s["translate_btn"], key="btn_translate"):
                    with st.spinner(s["translating"].format(lang=target)):
                        translated, err = translate_text(edited, TRANSLATE_LANGUAGES[target])
                    if err: st.error(s["translate_fail"].format(err=err))
                    else:
                        st.session_state["translated_text"] = translated
                        st.success(s["translate_success"])
                if st.session_state.get("translated_text"):
                    trans = st.session_state["translated_text"]
                    st.text_area(s["translated_label"].format(lang=target), value=trans,
                                 height=200, key="trans_display")
                    tc1, tc2 = st.columns(2)
                    with tc1:
                        d,e = export_txt(trans, f"translated_{target}")
                        if not e: st.download_button(s["dl_trans_txt"], d, f"translated_{target}.txt",
                                                     "text/plain", key="dl_tt", use_container_width=True)
                    with tc2:
                        d,e = export_pdf(trans, f"translated_{target}")
                        if not e: st.download_button(s["dl_trans_pdf"], d, f"translated_{target}.pdf",
                                                     "application/pdf", key="dl_tp", use_container_width=True)
        else:
            st.markdown(f"""
            <div class="p2d-card" style="text-align:center;padding:3rem 1.5rem;margin-top:1rem;">
                <div style="font-size:2.5rem;margin-bottom:1rem;">✨</div>
                <div style="font-weight:600;font-size:1.05rem;margin-bottom:.6rem;">{s['empty_state_title']}</div>
                <div class="help-text">{s['empty_state_desc'].replace(chr(10),'<br>')}</div>
            </div>""", unsafe_allow_html=True)


# ── TAB 2: Image Tools ────────────────────────────────────────────────────────

def tab_image_tools(s: dict) -> None:
    st.markdown("Upload an image and adjust it before sending to OCR.")
    uploaded = st.file_uploader("Upload image to edit", type=ALLOWED_EXT, key="img_tool_upload")
    if not uploaded:
        return

    uploaded.seek(0)
    raw_bytes = uploaded.read()
    orig_img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")

    st.markdown('<div class="p2d-section">Adjustments</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        rotate  = st.slider("🔄 Rotate (degrees)", -180, 180, 0, 1, key="it_rotate")
        bright  = st.slider("☀️ Brightness", 0.3, 2.5, 1.0, 0.05, key="it_bright")
        contrast= st.slider("🎨 Contrast",   0.3, 3.0, 1.0, 0.05, key="it_contrast")
    with c2:
        sharp   = st.slider("🔪 Sharpness",  0.0, 4.0, 1.0, 0.1,  key="it_sharp")
        denoise = st.toggle("🧹 Denoise (bilateral filter)", value=False, key="it_denoise")
        gray    = st.toggle("⬛ Grayscale preview", value=False, key="it_gray")

    st.markdown('<div class="p2d-section">Crop (%)</div>', unsafe_allow_html=True)
    cc1, cc2, cc3, cc4 = st.columns(4)
    with cc1: crop_l = st.number_input("Left",   0, 49, 0, key="cr_l")
    with cc2: crop_t = st.number_input("Top",    0, 49, 0, key="cr_t")
    with cc3: crop_r = st.number_input("Right",  51,100,100,key="cr_r")
    with cc4: crop_b = st.number_input("Bottom", 51,100,100,key="cr_b")

    edited_img = apply_all(
        orig_img,
        rotate_deg=rotate, brightness=bright, contrast=contrast,
        sharpness=sharp, denoise=denoise, grayscale=gray,
        crop_left=crop_l, crop_top=crop_t, crop_right=crop_r, crop_bottom=crop_b,
    )

    left_p, right_p = st.columns(2)
    with left_p:
        st.caption("Original")
        st.image(orig_img, width=700)
    with right_p:
        st.caption("✏️ Edited Preview")
        st.image(edited_img, width=700)

    st.markdown("<br>", unsafe_allow_html=True)
    bc1, bc2 = st.columns(2)
    with bc1:
        edited_bytes = pil_to_bytes(edited_img)
        st.download_button("💾 Download edited image", edited_bytes,
                           f"edited_{uploaded.name}", "image/png",
                           use_container_width=True)
    with bc2:
        if st.button("➡️ Use this image for OCR", type="primary", use_container_width=True):
            st.session_state["img_edited"] = pil_to_bytes(edited_img)
            st.session_state["img_edit_source"] = uploaded.name
            st.success("✅ Edited image saved! Go to the **OCR** tab and upload the same file.")


# ── TAB 3: Batch OCR ─────────────────────────────────────────────────────────

def tab_batch(s: dict) -> None:
    st.markdown("Upload multiple images — Pic2Docs will OCR all of them and combine the results.")
    files = st.file_uploader("Upload images (multiple)", type=ALLOWED_EXT,
                              accept_multiple_files=True, key="batch_upload")
    if not files:
        return

    lang_name = st.selectbox(s["ocr_lang_label"], list(LANGUAGE_MAP.keys()), key="batch_lang")
    lang_code = LANGUAGE_MAP[lang_name]

    if st.button(f"🚀 Process all {len(files)} images", type="primary", key="btn_batch"):
        progress = st.progress(0)
        status   = st.empty()
        file_data = []
        for f in files:
            f.seek(0)
            file_data.append((f.name, f.read()))

        def on_progress(cur, tot, fname):
            progress.progress(cur / tot)
            status.markdown(f"Processing **{fname}** ({cur}/{tot})…")

        results = run_batch_ocr(file_data, lang_code, on_progress)
        progress.progress(1.0)
        status.empty()

        stats = batch_stats(results)
        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-chip"><span>Total</span>{stats['total']}</div>
            <div class="stat-chip"><span>✅ Success</span>{stats['success']}</div>
            <div class="stat-chip"><span>❌ Failed</span>{stats['failed']}</div>
            <div class="stat-chip"><span>Avg Conf</span>{stats['avg_conf']}%</div>
            <div class="stat-chip"><span>Words</span>{stats['total_words']:,}</div>
        </div>""", unsafe_allow_html=True)

        for item in results:
            icon = "✅" if item.success else "❌"
            conf = f"{int(item.result.confidence*100)}%" if item.success else "—"
            with st.expander(f"{icon} {item.filename}  —  Confidence: {conf}"):
                if item.success:
                    st.text_area("", value=item.result.text, height=180,
                                 key=f"batch_text_{item.filename}", label_visibility="collapsed")
                else:
                    st.error(f"Error: {item.error}")

        combined = combine_results_txt(results)
        st.markdown('<div class="p2d-section">Export Combined Results</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📃 Download combined TXT", combined,
                               "batch_results.txt", "text/plain", use_container_width=True)
        with c2:
            all_text = "\n\n".join(i.result.text for i in results if i.success)
            d, e = export_docx(all_text, "batch_results")
            if not e:
                st.download_button("📝 Download combined Word", d,
                                   "batch_results.docx",
                                   "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                   use_container_width=True)


# ── TAB 4: History ────────────────────────────────────────────────────────────

def tab_history(s: dict) -> None:
    history = get_history()
    if not history:
        st.info("No history yet. Extract text from an image to start building your history.")
        return

    hc1, hc2, hc3 = st.columns([2,1,1])
    with hc1:
        st.markdown(f"**{len(history)} items** in this session")
    with hc2:
        d = export_history_txt()
        st.download_button("📃 Export all TXT", d, "history.txt", "text/plain", use_container_width=True)
    with hc3:
        d = export_history_json()
        st.download_button("🗂 Export JSON", d, "history.json", "application/json", use_container_width=True)

    if st.button("🗑 Clear all history", key="clear_hist"):
        clear_history(); st.rerun()

    st.markdown("---")
    for entry in history:
        with st.expander(f"📄 {entry.filename}  ·  {entry.timestamp}  ·  {entry.language}  ·  {int(entry.confidence*100)}% confidence"):
            st.text_area("", value=entry.text, height=160,
                         key=f"hist_{entry.id}", label_visibility="collapsed")
            hb1, hb2, hb3, hb4 = st.columns(4)
            with hb1:
                d,e = export_txt(entry.text, entry.filename)
                if not e: st.download_button("📃 TXT", d, f"{entry.filename}_hist.txt",
                                             "text/plain", key=f"h_txt_{entry.id}", use_container_width=True)
            with hb2:
                d,e = export_pdf(entry.text, entry.filename)
                if not e: st.download_button("📄 PDF", d, f"{entry.filename}_hist.pdf",
                                             "application/pdf", key=f"h_pdf_{entry.id}", use_container_width=True)
            with hb3:
                if st.button("↩ Restore to OCR", key=f"h_restore_{entry.id}", use_container_width=True):
                    st.session_state.update({"edited_text": entry.text})
                    st.success("Restored! Switch to the OCR tab.")
            with hb4:
                if st.button("🗑 Delete", key=f"h_del_{entry.id}", use_container_width=True):
                    delete_entry(entry.id); st.rerun()


# ── TAB 5: Summarize & Keywords ───────────────────────────────────────────────

def tab_summarize(s: dict) -> None:
    text = st.session_state.get("edited_text", "").strip()
    if not text:
        st.info("Extract text from an image first (OCR tab), then come here to analyse it.")
        return

    wc = len(text.split())
    lc = len([l for l in text.split("\n") if l.strip()])
    st.markdown(f'<div class="stat-row">'
                f'<div class="stat-chip"><span>Words</span>{wc:,}</div>'
                f'<div class="stat-chip"><span>Lines</span>{lc:,}</div>'
                f'<div class="stat-chip"><span>Chars</span>{len(text):,}</div>'
                f'</div>', unsafe_allow_html=True)

    # Keywords
    st.markdown('<div class="p2d-section">🔑 Top Keywords</div>', unsafe_allow_html=True)
    top_n = st.slider("Number of keywords", 5, 20, 10, key="kw_n")
    keywords = extract_keywords(text, top_n=top_n)
    kw_html = " ".join(f'<span class="kw-pill">{k}</span>' for k in keywords)
    st.markdown(f'<div style="margin:0.5rem 0 1rem">{kw_html}</div>', unsafe_allow_html=True)
    kw_txt = ", ".join(keywords)
    st.download_button("📃 Download keywords", kw_txt.encode(), "keywords.txt",
                       "text/plain", key="dl_kw")

    # Summary
    st.markdown('<div class="p2d-section">📝 AI Summary (Extractive)</div>', unsafe_allow_html=True)
    max_sent = st.slider("Summary length (sentences)", 2, 8, 4, key="sum_n")
    if wc < 30:
        st.warning("Text is too short to summarise meaningfully.")
    else:
        summary = summarize_text(text, max_sentences=max_sent)
        st.text_area("Summary (editable)", value=summary, height=180, key="summary_box")
        sc1, sc2 = st.columns(2)
        with sc1:
            d,e = export_txt(summary, "summary")
            if not e: st.download_button("📃 Summary TXT", d, "summary.txt", "text/plain",
                                         key="dl_sum_txt", use_container_width=True)
        with sc2:
            d,e = export_pdf(summary, "summary")
            if not e: st.download_button("📄 Summary PDF", d, "summary.pdf", "application/pdf",
                                         key="dl_sum_pdf", use_container_width=True)

    # Reading stats
    st.markdown('<div class="p2d-section">📊 Reading Stats</div>', unsafe_allow_html=True)
    reading_min = round(wc / 200, 1)
    avg_word_len = round(sum(len(w) for w in text.split()) / max(wc, 1), 1)
    sentences = len([s for s in text.replace("!","。").replace("?","。").split(".") if s.strip()])
    st.markdown(f"""
    <div class="p2d-card">
        <div class="stat-row">
            <div class="stat-chip"><span>Reading time</span>~{reading_min} min</div>
            <div class="stat-chip"><span>Sentences</span>{sentences}</div>
            <div class="stat-chip"><span>Avg word length</span>{avg_word_len} chars</div>
            <div class="stat-chip"><span>Unique words</span>{len(set(text.lower().split())):,}</div>
        </div>
    </div>""", unsafe_allow_html=True)


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    _init()

    # Auth imports
    from auth.auth_manager   import is_logged_in, get_profile, logout, check_usage_limit, increment_usage, save_ocr_history
    from auth.login_page     import render_login_page
    from pricing_page        import render_pricing_page
    from admin_dashboard     import render_admin_dashboard, is_admin

    # Show login page if not logged in
    if not is_logged_in():
        _css()
        render_login_page()
        return

    profile = get_profile()
    plan    = profile.get("plan", "free") if profile else "free"
    used    = profile.get("images_used", 0) if profile else 0
    limit   = profile.get("images_limit", 10) if profile else 10

    with st.sidebar:
        st.markdown(f'<div class="p2d-logo">📄 {APP_NAME} <span class="p2d-badge">v{APP_VERSION}</span></div>',
                    unsafe_allow_html=True)
        st.markdown("---")

        # User info
        email = profile.get("email", "") if profile else ""
        name  = profile.get("full_name", email.split("@")[0]) if profile else ""
        plan_color = {"free":"#8888A8","basic":"#22C87A","pro":"#6C63FF"}.get(plan,"#8888A8")
        st.markdown(f"""
        <div style="font-size:.85rem;margin-bottom:.5rem;">
            👤 <b>{name}</b><br>
            <span style="font-size:.75rem;color:{plan_color};font-weight:600;text-transform:uppercase;">
                {plan} plan
            </span>
        </div>
        <div style="font-size:.77rem;color:#8888A8;margin-bottom:.5rem;">
            🖼 {used} / {'∞' if limit > 9999 else limit} images used
        </div>
        """, unsafe_allow_html=True)

        if plan == "free" and used >= limit:
            st.warning("⚠️ Limit reached! Upgrade to continue.")

        st.markdown("---")
        lang = st.selectbox("🌐 Language",
                            list(UI_STRINGS.keys()),
                            index=list(UI_STRINGS.keys()).index(st.session_state["ui_lang"]),
                            key="ui_lang_select", label_visibility="collapsed")
        st.session_state["ui_lang"] = lang
        st.markdown("---")

        hist = get_history()
        cur_text = st.session_state.get("edited_text","")
        st.markdown(f"""
        <div style="font-size:.77rem;color:#8888A8;line-height:2;">
        🗂 History: <b style="color:#E8E8F0">{len(hist)}</b> items<br>
        📝 Words: <b style="color:#E8E8F0">{len(cur_text.split()):,}</b>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

    s = get_strings(st.session_state["ui_lang"])
    _css(rtl=is_rtl(st.session_state["ui_lang"]))

    # Build tabs based on role
    tab_labels = ["📄 OCR","🖊 Image Tools","📦 Batch OCR","🕘 History","🔍 Summarize","💎 Pricing"]
    if is_admin():
        tab_labels.append("🛠 Admin")

    tabs = st.tabs(tab_labels)

    with tabs[0]: tab_ocr(s)
    with tabs[1]: tab_image_tools(s)
    with tabs[2]: tab_batch(s)
    with tabs[3]: tab_history(s)
    with tabs[4]: tab_summarize(s)
    with tabs[5]: render_pricing_page()
    if is_admin() and len(tabs) > 6:
        with tabs[6]: render_admin_dashboard()


if __name__ == "__main__":
    main()
