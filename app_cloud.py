import streamlit as st
import requests

# Config
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
        return result["ParsedResults"][0]["ParsedText"]
    except Exception as e:
        return f"❌ OCR Failed: {str(e)}"

# UI
st.set_page_config(page_title="Pic2Docs", layout="centered")
st.title("📸 Pic2Docs - Convert Image to Text")
st.markdown("Upload an image and extract text using OCR API.\n\nSupports multiple languages 🌐.")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

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

        st.success("✅ Text Extraction Complete!")
        st.text_area("📄 Extracted Text", extracted_text, height=300)
        st.download_button("📥 Download Text", extracted_text, file_name="extracted_text.txt")
else:
    st.info("Please upload an image file to begin.")
