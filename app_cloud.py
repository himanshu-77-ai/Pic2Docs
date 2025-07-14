import streamlit as st
from fpdf import FPDF
from docx import Document
from openpyxl import Workbook
import textwrap
from PIL import Image, ImageDraw, ImageFont

st.title("📸 Pic2Docs (Demo) - Convert Image to Text")

# Upload disabled in demo
st.info("This is a demo version. Upload disabled. Full OCR version works locally.")

# Sample extracted text
text = "This is demo extracted text from an image.\nFeel free to download it in any format."

st.text_area("Extracted Text", text, height=300)

# Download as .txt
st.download_button("Download Text File", text, file_name="output.txt")

# PDF Download
if st.button("Download as Notebook-style PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    lines = text.split('\n')
    for line in lines:
        pdf.multi_cell(0, 10, txt=line)
    pdf.output("output.pdf")
    with open("output.pdf", "rb") as f:
        st.download_button("Click to Download Notebook PDF", f, file_name="notebook_text.pdf")

# Word Download
if st.button("Download as Word File"):
    doc = Document()
    doc.add_heading("Extracted Text", 0)
    for line in text.split('\n'):
        doc.add_paragraph(line)
    doc.save("output.docx")
    with open("output.docx", "rb") as f:
        st.download_button("Click to Download Word File", f, file_name="extracted_text.docx")

# Excel Download
if st.button("Download as Excel File"):
    wb = Workbook()
    ws = wb.active
    ws.title = "ExtractedText"
    for idx, line in enumerate(text.split('\n'), start=1):
        ws.cell(row=idx, column=1, value=line)
    wb.save("output.xlsx")
    with open("output.xlsx", "rb") as f:
        st.download_button("Click to Download Excel File", f, file_name="extracted_text.xlsx")

# Image Download
if st.button("Download as Notebook-style Image"):
    img_width = 800
    img_height = 1200
    image = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    margin = 40
    offset = 40
    line_height = 20
    wrapped_text = textwrap.wrap(text, width=100)
    for line in wrapped_text:
        draw.text((margin, offset), line, font=font, fill='black')
        offset += line_height
    image.save("output_image.png")
    with open("output_image.png", "rb") as f:
        st.download_button("Click to Download Notebook Image", f, file_name="notebook_text.png")
