import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from io import BytesIO
from fpdf import FPDF
from docx import Document
import pandas as pd
import os

# ------------------------ OCR SETUP ------------------------
@st.cache_resource
def load_ocr_model():
    try:
        # Load model with Bengali + English support
        return easyocr.Reader(['bn','en'], gpu=False)
    except Exception as e:
        st.error(f"Model loading error: {str(e)}")
        return None

def ocr_image(image_file):
    try:
        reader = load_ocr_model()
        if reader is None:
            return "OCR model failed to load"
        
        image = Image.open(image_file)
        result = reader.readtext(np.array(image), detail=0, paragraph=True)
        return '\n'.join(result) if result else "No text found"
    except Exception as e:
        return f"OCR Error: {str(e)}"

# ------------------------ EXPORT FUNCTIONS ------------------------
def convert_to_pdf(text):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Add UTF-8 font (supports Bengali/Hindi)
        pdf.add_font('ArialUnicode', '', 'arial-unicode-ms.ttf', uni=True)
        pdf.set_font('ArialUnicode', '', 12)
        
        for line in text.split('\n'):
            pdf.cell(200, 10, txt=line, ln=True)
            
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        st.error(f"PDF creation failed: {str(e)}")
        return None

def convert_to_word(text):
    try:
        doc = Document()
        doc.add_paragraph(text)
        buffer = BytesIO()
        doc.save(buffer)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Word export failed: {str(e)}")
        return None

def convert_to_excel(text):
    try:
        lines = text.split('\n')
        df = pd.DataFrame({"Extracted Text": lines})
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Excel export failed: {str(e)}")
        return None

# ------------------------ UI ------------------------
st.set_page_config(page_title="Pic2Docs", layout="wide")
st.title("📄 Pic2Docs - Image to Text Converter")

# Check for font file
if not os.path.exists("arial-unicode-ms.ttf"):
    st.warning("Please add 'arial-unicode-ms.ttf' to your project folder")

uploaded_file = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    with col2:
        lang = st.selectbox("Select language", ["English", "Bengali", "Hindi"])
        lang_code = "en" if lang == "English" else "bn" if lang == "Bengali" else "hi"

    if st.button("Extract Text", type="primary"):
        with st.spinner("Processing..."):
            extracted_text = ocr_image(uploaded_file)
            
        st.subheader("Extracted Text")
        st.text_area("", extracted_text, height=300, label_visibility="collapsed")

        if extracted_text and not extracted_text.startswith("Error"):
            # Download buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if pdf_data := convert_to_pdf(extracted_text):
                    st.download_button("Download PDF", pdf_data, "text.pdf")
            with col2:
                if word_data := convert_to_word(extracted_text):
                    st.download_button("Download Word", word_data, "text.docx")
            with col3:
                if excel_data := convert_to_excel(extracted_text):
                    st.download_button("Download Excel", excel_data, "text.xlsx")
else:
    st.info("Please upload an image file")
