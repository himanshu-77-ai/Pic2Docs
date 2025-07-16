import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from fpdf import FPDF
from docx import Document
from openpyxl import Workbook
from deep_translator import GoogleTranslator
import textwrap

# 🚫 DO NOT set tesseract path for Streamlit Cloud
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# App title
st.set_page_config(page_title="Pic2Docs", page_icon="📸")
st.title("📸 Pic2Docs - Convert Image to Text")

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

# Session state for text
if "extracted_text" not in st.session_state:
    st.session_state["extracted_text"] = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Language selection including digit-only mode
    lang = st.selectbox("Select language", ["English", "Hindi", "Digits Only"])

    if lang == "English":
        lang_code = "eng"
        config = ""
    elif lang == "Hindi":
        lang_code = "hin"
        config = ""
    else:
        lang_code = "eng"  # Use English trained model for digits
        config = "--psm 6 outputbase digits"

    if st.button("Extract Text"):
        with st.spinner("Extracting text..."):
            try:
                extracted = pytesseract.image_to_string(image, lang=lang_code, config=config)
                st.session_state["extracted_text"] = extracted
                st.success("Text extracted successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

# Show extracted text
text = st.session_state["extracted_text"]
if text:
    st.text_area("📝 Extracted Text", text, height=300)
    st.download_button("⬇️ Download Text File", text, file_name="output.txt")

    # PDF
    if st.button("Download as Notebook-style PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.set_font("DejaVu", size=12)
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        for line in text.split('\n'):
            pdf.multi_cell(0, 10, txt=line)
        pdf.output("output.pdf")
        with open("output.pdf", "rb") as f:
            st.download_button("Download Notebook PDF", f, file_name="notebook_text.pdf")
        os.remove("output.pdf")

    # Word
    if st.button("Download as Word File"):
        doc = Document()
        doc.add_heading("Extracted Text", 0)
        for line in text.split('\n'):
            doc.add_paragraph(line)
        doc.save("output.docx")
        with open("output.docx", "rb") as f:
            st.download_button("Download Word File", f, file_name="extracted_text.docx")
        os.remove("output.docx")

    # Excel
    if st.button("Download as Excel File"):
        wb = Workbook()
        ws = wb.active
        ws.title = "ExtractedText"
        for idx, line in enumerate(text.split('\n'), start=1):
            ws.cell(row=idx, column=1, value=line)
        wb.save("output.xlsx")
        with open("output.xlsx", "rb") as f:
            st.download_button("Download Excel File", f, file_name="extracted_text.xlsx")
        os.remove("output.xlsx")

    # Notebook-style Image
    if st.button("Download as Notebook-style Image"):
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
            st.download_button("Download Notebook Image", f, file_name="notebook_text.png")
        os.remove(image_path)

# Translation
target_lang = st.selectbox("Translate Text To", ["None", "English", "Hindi", "French", "German", "Spanish"])
if target_lang != "None" and text.strip() != "":
    try:
        translated_text = GoogleTranslator(source='auto', target=target_lang.lower()).translate(text)
        st.text_area("🌍 Translated Text", translated_text, height=300)
        st.download_button("Download Translated Text", translated_text, file_name=f"translated_text_{target_lang}.txt")
    except Exception as e:
        st.error(f"Translation failed: {e}")
