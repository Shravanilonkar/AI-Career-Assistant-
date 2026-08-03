import streamlit as st
from langchain_groq import ChatGroq


def get_llm():
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        api_key=st.secrets["GROQ_API_KEY"],
    )
    return llm