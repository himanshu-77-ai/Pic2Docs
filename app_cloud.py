import os
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"


import streamlit as st
from PIL import Image
import pytesseract

# ✅ Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from fpdf import FPDF
from docx import Document
from openpyxl import Workbook
from deep_translator import GoogleTranslator
import textwrap
from PIL import ImageDraw, ImageFont

# Streamlit App Title
st.title("📸 Pic2Docs - Convert Image to Text")

# Upload Image
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

# Session state for text storage
if "extracted_text" not in st.session_state:
    st.session_state["extracted_text"] = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    lang = st.selectbox("Select language", ["English", "Hindi"])
    lang_code = "eng" if lang == "English" else "hin"

    if st.button("Extract Text"):
        with st.spinner("Extracting text..."):
            try:
                extracted = pytesseract.image_to_string(image, lang=lang_code)
                st.session_state["extracted_text"] = extracted
                st.success("Text extracted successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

# Show extracted text
text = st.session_state["extracted_text"]
if text:
    st.text_area("Extracted Text", text, height=300)
    st.download_button("Download Text File", text, file_name="output.txt")

    # PDF Download
    if st.button("Download as Notebook-style PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)  # Make sure DejaVuSans.ttf is in same folder
        pdf.set_font("DejaVu", size=12)
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)

        lines = text.split('\n')
        for line in lines:
            pdf.multi_cell(0, 10, txt=line)

        pdf.output("output.pdf")
        with open("output.pdf", "rb") as f:
            st.download_button("Click to Download Notebook PDF", f, file_name="notebook_text.pdf")
        os.remove("output.pdf")

    # Word Download
    if st.button("Download as Word File"):
        if text.strip() != "":
            doc = Document()
            doc.add_heading("Extracted Text", 0)
            for line in text.split('\n'):
                doc.add_paragraph(line)
            doc.save("output.docx")
            with open("output.docx", "rb") as f:
                st.download_button("Click to Download Word File", f, file_name="extracted_text.docx")
            os.remove("output.docx")
        else:
            st.warning("No text to convert into Word file.")

    # Excel Download
    if st.button("Download as Excel File"):
        if text.strip() != "":
            wb = Workbook()
            ws = wb.active
            ws.title = "ExtractedText"
            lines = text.split('\n')
            for idx, line in enumerate(lines, start=1):
                ws.cell(row=idx, column=1, value=line)
            wb.save("output.xlsx")
            with open("output.xlsx", "rb") as f:
                st.download_button("Click to Download Excel File", f, file_name="extracted_text.xlsx")
            os.remove("output.xlsx")
        else:
            st.warning("No text available to convert into Excel.")

    # Notebook-style Image
    if st.button("Download as Notebook-style Image"):
        if text.strip() != "":
            img_width = 800
            img_height = 1200
            img = Image.new('RGB', (img_width, img_height), color='white')
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            margin = 40
            offset = 40
            line_height = 20
            wrapped_text = textwrap.wrap(text, width=100)
            for line in wrapped_text:
                draw.text((margin, offset), line, font=font, fill='black')
                offset += line_height
            image_path = "output_image.png"
            img.save(image_path)
            with open(image_path, "rb") as f:
                st.download_button("Click to Download Notebook Image", f, file_name="notebook_text.png")
            os.remove(image_path)
        else:
            st.warning("No text available to convert into Image.")

# Translation
target_lang = st.selectbox("Translate Text To", ["None", "English", "Hindi", "French", "German", "Spanish"])
if target_lang != "None":
    try:
        translated_text = GoogleTranslator(source='auto', target=target_lang.lower()).translate(text)
        st.text_area("Translated Text", translated_text, height=300)
        st.download_button("Download Translated Text", translated_text, file_name=f"translated_text_{target_lang}.txt")
    except Exception as e:
        st.error(f"Translation failed: {e}")
