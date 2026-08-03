from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_SIZE
from config import CHUNK_OVERLAP


def split_text(text):
    """
    Split extracted text into chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )

    chunks = splitter.split_text(text)

    return chunks