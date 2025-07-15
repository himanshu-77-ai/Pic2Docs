import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from fpdf import FPDF
from docx import Document
from openpyxl import Workbook
import textwrap
from PIL import ImageDraw, ImageFont

# 🔑 Your OCR.space API key
OCR_API_KEY = "K82703136888957"

st.title("📸 Pic2Docs (Cloud) - Convert Image to Text")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if "extracted_text" not in st.session_state:
    st.session_state["extracted_text"] = ""

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    lang = st.selectbox("Select OCR Language", ["English", "Hindi"])
    lang_code = "eng" if lang == "English" else "hin"

    if st.button("Extract Text"):
        with st.spinner("Extracting text using OCR API..."):
            try:
                img_bytes = BytesIO()
                image.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                response = requests.post(
                    'https://api.ocr.space/parse/image',
                    files={"filename": img_bytes},
                    data={"language": lang_code, "isOverlayRequired": False},
                    headers={"apikey": OCR_API_KEY}
                )

                result = response.json()
                extracted = result['ParsedResults'][0]['ParsedText']
                st.session_state["extracted_text"] = extracted
                st.success("Text extracted successfully!")

            except Exception as e:
                st.error(f"OCR failed: {e}")

# Display and download section
text = st.session_state["extracted_text"]
if text:
    st.text_area("Extracted Text", text, height=300)
    st.download_button("⬇️ Download as .txt", text, file_name="output.txt")

    # PDF download
    if st.button("⬇️ Download as PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        lines = text.split('\n')
        for line in lines:
            pdf.multi_cell(0, 10, txt=line)
        pdf.output("output.pdf")
        with open("output.pdf", "rb") as f:
            st.download_button("Download PDF", f, file_name="extracted_text.pdf")

    # Word file
    if st.button("⬇️ Download as Word"):
        doc = Document()
        doc.add_heading("Extracted Text", 0)
        for line in text.split('\n'):
            doc.add_paragraph(line)
        doc.save("output.docx")
        with open("output.docx", "rb") as f:
            st.download_button("Download Word File", f, file_name="extracted_text.docx")

    # Excel file
    if st.button("⬇️ Download as Excel"):
        wb = Workbook()
        ws = wb.active
        lines = text.split('\n')
        for idx, line in enumerate(lines, start=1):
            ws.cell(row=idx, column=1, value=line)
        wb.save("output.xlsx")
        with open("output.xlsx", "rb") as f:
            st.download_button("Download Excel File", f, file_name="extracted_text.xlsx")

    # Image file (notebook style)
    if st.button("⬇️ Download as Notebook Image"):
        img_width, img_height = 800, 1200
        image = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        margin, offset, line_height = 40, 40, 20
        wrapped_text = textwrap.wrap(text, width=100)
        for line in wrapped_text:
            draw.text((margin, offset), line, font=font, fill='black')
            offset += line_height
        image.save("output_img.png")
        with open("output_img.png", "rb") as f:
            st.download_button("Download Image", f, file_name="notebook_text.png")

else:
    st.info("Upload an image and click 'Extract Text' to begin.")
