import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
from docx import Document
import base64
from io import BytesIO
import openpyxl

# ----------------- OCR Function -----------------
def ocr_space_file(image_file, api_key='K82703136888957'):
    payload = {
        'isOverlayRequired': False,
        'apikey': api_key,
        'language': 'eng',
    }
    files = {
        'file': image_file,
    }
    response = requests.post('https://api.ocr.space/parse/image',
                             files=files,
                             data=payload)
    result = response.json()
    try:
        return result['ParsedResults'][0]['ParsedText']
    except:
        return "Error reading text."

# ----------------- PDF Generator -----------------
def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)  # ✅ Default font (no error)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# ----------------- Word Generator -----------------
def generate_word(text):
    doc = Document()
    doc.add_heading("Extracted Text", 0)
    for line in text.split('\n'):
        doc.add_paragraph(line)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ----------------- Excel Generator -----------------
def generate_excel(text):
    lines = text.strip().split('\n')
    df = pd.DataFrame({'Extracted Text': lines})
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

# ----------------- Streamlit UI -----------------
st.set_page_config(page_title="Pic2Docs", layout="centered")
st.title("📸 Pic2Docs - Image to Text Extractor")

uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    st.info("Extracting text...")

    extracted_text = ocr_space_file(uploaded_file)  # 👈 Key is already inside the function

    st.subheader("📝 Extracted Text")
    st.text_area("Result", extracted_text, height=250)

    # ----------------- Download Buttons -----------------
    col1, col2, col3 = st.columns(3)
    with col1:
        pdf_file = generate_pdf(extracted_text)
        st.download_button(label="📄 Download PDF",
                           data=pdf_file,
                           file_name="output.pdf",
                           mime="application/pdf")

    with col2:
        word_file = generate_word(extracted_text)
        st.download_button(label="📝 Download Word",
                           data=word_file,
                           file_name="output.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    with col3:
        excel_file = generate_excel(extracted_text)
        st.download_button(label="📊 Download Excel",
                           data=excel_file,
                           file_name="output.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
