from langchain_ollama import ChatOllama

from config import LLM_MODEL


def load_llm():
    """
    Load Ollama LLM.
    """

    llm = ChatOllama(
        model=LLM_MODEL,
        temperature=0
    )

    return llm