import easyocr

reader = easyocr.Reader(["en"])


def extract_text_from_image(image_path):
    """
    Extract text from image using OCR.
    """

    results = reader.readtext(image_path)

    text = ""

    for result in results:

        text += result[1] + "\n"

    return text