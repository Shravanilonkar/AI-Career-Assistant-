from langchain_huggingface import HuggingFaceEmbeddings

from config import EMBEDDING_MODEL


def load_embedding_model():
    """
    Load Hugging Face embedding model.
    """

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    return embeddings