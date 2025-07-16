import streamlit as st
import requests
from fpdf import FPDF
from docx import Document
import pandas as pd
from io import BytesIO

API_KEY = "K82703136888957"
OCR_API_URL = "https://api.ocr.space/parse/image"

def ocr_space_image(image_file, api_key=API_KEY, language="eng"):
    try:
        response = requests.post(
            OCR_API_URL,
            files={"filename": image_file},
            data={
                "apikey": api_key,
                "language": language,
                "isOverlayRequired": False,
            },
        )
        result = response.json()
        if "ParsedResults" in result:
            return result["ParsedResults"][0]["ParsedText"]
        else:
            return f"❌ OCR Failed: {result.get('ErrorMessage', 'Unknown error')}"
    except Exception as e:
        return f"❌ OCR Failed: {str(e)}"

def convert_to_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True)
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

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

# Streamlit UI
st.set_page_config(page_title="Pic2Docs", layout="centered")
st.title("📸 Pic2Docs - Convert Image to Text")
st.markdown("Upload an image and extract text using OCR API.\n\nSupports multiple languages 🌐.")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    lang_display = st.selectbox("Select image language", ["English", "Hindi", "French", "Spanish", "German", "Bengali"])
    lang_map = {
        "English": "eng",
        "Hindi": "hin",
        "French": "fra",
        "Spanish": "spa",
        "German": "ger",
        "Bengali": "ben"
    }
    selected_lang_code = lang_map[lang_display]

    if st.button("📝 Extract Text"):
        with st.spinner("Processing image... please wait ⏳"):
            extracted_text = ocr_space_image(uploaded_file, language=selected_lang_code)

        st.text_area("📄 Extracted Text", extracted_text, height=300)
        
        if not extracted_text.startswith("❌"):
            # Download buttons
            st.download_button("📥 Download .txt", extracted_text, file_name="text.txt")
            st.download_button("📄 Download PDF", convert_to_pdf(extracted_text), file_name="text.pdf")
            st.download_button("📝 Download Word", convert_to_word(extracted_text), file_name="text.docx")
            st.download_button("📊 Download Excel", convert_to_excel(extracted_text), file_name="text.xlsx")
        else:
            st.error(extracted_text)
else:
    st.info("Please upload an image file to begin.")
