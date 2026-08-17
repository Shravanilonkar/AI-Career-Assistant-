import streamlit as st
from langchain_groq import ChatGroq


def load_llm():
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=st.secrets["GROQ_API_KEY"],
    )
    return llm