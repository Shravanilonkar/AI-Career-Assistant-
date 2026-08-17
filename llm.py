import streamlit as st
from langchain_groq import ChatGroq


def load_llm():
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        api_key=st.secrets["GROQ_API_KEY"],
    )
    return llm