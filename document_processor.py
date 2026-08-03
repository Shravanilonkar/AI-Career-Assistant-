from pdf_loader import extract_text_from_pdf
from image_loader import extract_text_from_image

from utils import is_pdf
from utils import is_image


def extract_document_text(file_path):
    """
    Detect file type and extract text.
    """

    if is_pdf(file_path):

        return extract_text_from_pdf(file_path)

    elif is_image(file_path):

        return extract_text_from_image(file_path)

    else:

        raise Exception("Unsupported File Type")