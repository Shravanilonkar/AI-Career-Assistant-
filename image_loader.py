
import easyocr
import streamlit as st
import time


@st.cache_resource(show_spinner=False)
def load_ocr_reader():
    print("OCR: Starting model initialization...")

    start = time.time()

    reader = easyocr.Reader(
        ["en"],
        gpu=False
    )

    print(f"OCR: Model loaded in {time.time() - start:.2f} seconds")

    return reader


def extract_text_from_image(image_path):

    print("OCR: Starting image extraction...")

    reader = load_ocr_reader()

    start = time.time()

    results = reader.readtext(image_path)

    print(f"OCR: Image extraction completed in {time.time() - start:.2f} seconds")

    text = "\n".join(
        result[1]
        for result in results
        if result[1].strip()
    )

    print(f"OCR: Extracted {len(text)} characters")

    return text
