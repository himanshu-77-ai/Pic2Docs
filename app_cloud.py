import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from io import BytesIO
from fpdf import FPDF
from docx import Document
import pandas as pd
import json

# ------------------------ OCR FUNCTION ------------------------
@st.cache_resource
def load_ocr_model():
    return easyocr.Reader(['en', 'hi', 'fr', 'es', 'de', 'bn'], gpu=False)

def ocr_image_local(image_file, language_code="en"):
    try:
        reader = load_ocr_model()
        image = Image.open(image_file)
        result = reader.readtext(np.array(image), detail=0, paragraph=True)
        return '\n'.join(result) if result else "❌ No text found."
    except Exception as e:
        return f"❌ OCR Failed: {str(e)}"

# ------------------------ EXPORT FUNCTIONS ------------------------

def convert_to_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True)
    return pdf.output(dest='S').encode('latin-1')

def convert_to_word(text):
    doc = Document()
    doc.add_paragraph(text)
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

def convert_to_excel(text):
    lines = text.split('\n')
    df = pd.DataFrame({"Extracted Text": lines})
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return buffer.getvalue()

def convert_to_ipynb(text):
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [text]
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 2
    }
    buffer = BytesIO()
    buffer.write(json.dumps(notebook, indent=2).encode('utf-8'))
    return buffer.getvalue()

# ------------------------ UI ------------------------

st.set_page_config(page_title="📸 Pic2Docs", layout="centered")
st.title("📸 Pic2Docs - Convert Image to Text")
st.markdown("Upload an image and extract text using OCR.\n\nWorks offline – No API needed ✅")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    lang_display = st.selectbox("Select image language", ["English", "Hindi", "French", "Spanish", "German", "Bengali"])
    lang_map = {
        "English": "en",
        "Hindi": "hi",
        "French": "fr",
        "Spanish": "es",
        "German": "de",
        "Bengali": "bn"
    }
    selected_lang_code = lang_map[lang_display]

    if st.button("📝 Extract Text"):
        with st.spinner("Processing image... please wait ⏳"):
            extracted_text = ocr_image_local(uploaded_file, selected_lang_code)

        st.text_area("📄 Extracted Text", extracted_text, height=300)

        if not extracted_text.startswith("❌"):
            st.download_button("📥 Download .txt", extracted_text, file_name="text.txt")
            st.download_button("📄 Download PDF", convert_to_pdf(extracted_text), file_name="text.pdf")
            st.download_button("📝 Download Word", convert_to_word(extracted_text), file_name="text.docx")
            st.download_button("📊 Download Excel", convert_to_excel(extracted_text), file_name="text.xlsx")
            st.download_button("📘 Download Notebook", convert_to_ipynb(extracted_text), file_name="text.ipynb")
        else:
            st.error(extracted_text)
else:
    st.info("Please upload an image file to begin.")
