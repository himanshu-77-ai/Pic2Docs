import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from fpdf import FPDF
from docx import Document
from openpyxl import Workbook
import textwrap
import os

st.set_page_config(page_title="📸 Pic2Docs", layout="centered")
st.title("📸 Pic2Docs - Convert Image to Text (Cloud Version)")

# Dummy OCR substitute for cloud (upload enabled)
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

# Session state for extracted text
if "extracted_text" not in st.session_state:
    st.session_state["extracted_text"] = ""

# Only demo functionality (no real OCR on Streamlit Cloud)
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    st.info("⚠️ This is a demo app. Real OCR runs only on local system due to Tesseract dependency.")
    
    # Simulated extracted text
    demo_text = "This is demo extracted text from the uploaded image.\nThank you for trying Pic2Docs!"
    st.session_state["extracted_text"] = demo_text
    st.success("Text extracted (simulated) successfully!")

# Show extracted/simulated text
text = st.session_state["extracted_text"]
if text:
    st.text_area("Extracted Text", text, height=300)
    st.download_button("⬇️ Download as Text File", text, file_name="output.txt")

    if st.button("📄 Download as PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font('Arial', '', '', uni=True)
        pdf.set_font("Arial", size=12)
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)

        for line in text.split('\n'):
            pdf.multi_cell(0, 10, txt=line)
        pdf.output("output.pdf")
        with open("output.pdf", "rb") as f:
            st.download_button("Click to Download PDF", f, file_name="notebook_text.pdf")
        os.remove("output.pdf")

    if st.button("📝 Download as Word File"):
        doc = Document()
        doc.add_heading("Extracted Text", 0)
        for line in text.split('\n'):
            doc.add_paragraph(line)
        doc.save("output.docx")
        with open("output.docx", "rb") as f:
            st.download_button("Download Word File", f, file_name="extracted_text.docx")
        os.remove("output.docx")

    if st.button("📊 Download as Excel File"):
        wb = Workbook()
        ws = wb.active
        ws.title = "ExtractedText"
        for idx, line in enumerate(text.split('\n'), start=1):
            ws.cell(row=idx, column=1, value=line)
        wb.save("output.xlsx")
        with open("output.xlsx", "rb") as f:
            st.download_button("Download Excel File", f, file_name="extracted_text.xlsx")
        os.remove("output.xlsx")

    if st.button("🖼️ Download as Notebook-style Image"):
        img_width, img_height = 800, 1200
        image = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        margin = 40
        offset = 40
        line_height = 20
        for line in textwrap.wrap(text, width=100):
            draw.text((margin, offset), line, font=font, fill='black')
            offset += line_height
        image_path = "output_image.png"
        image.save(image_path)
        with open(image_path, "rb") as f:
            st.download_button("Download Image", f, file_name="notebook_text.png")
        os.remove(image_path)
else:
    st.warning("Upload an image to begin.")
