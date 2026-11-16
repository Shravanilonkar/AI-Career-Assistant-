
import easyocr
import streamlit as st


@st.cache_resource(show_spinner=False)
def load_ocr_reader():
    """Load OCR model once and reuse it."""
    return easyocr.Reader(
        ["en"],
        gpu=False
    )


def extract_text_from_image(image_path):
    """
    Extract text from an image using cached EasyOCR.
    """

    reader = load_ocr_reader()

    results = reader.readtext(image_path)

    text = "\n".join(
        result[1]
        for result in results
        if result[1].strip()
    )

    return text
