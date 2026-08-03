import os

from langchain_community.vectorstores import FAISS

from config import VECTOR_DB_PATH


def create_vector_store(chunks, embeddings):
    """
    Create and save FAISS vector database.
    """

    vector_store = FAISS.from_texts(
        texts=chunks,
        embedding=embeddings
    )

    os.makedirs(
        VECTOR_DB_PATH,
        exist_ok=True
    )

    vector_store.save_local(
        VECTOR_DB_PATH
    )

    return vector_store


def load_vector_store(embeddings):
    """
    Load saved FAISS vector database.
    """

    vector_store = FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vector_store