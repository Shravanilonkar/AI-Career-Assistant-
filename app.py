import streamlit as st
from streamlit_mic_recorder import mic_recorder
from file_handler import save_uploaded_file
from document_processor import extract_document_text

from text_splitter import split_text

from embeddings import load_embedding_model
from vector_store import create_vector_store

from llm import load_llm
from chatbot import create_chatbot

from resume_analyzer import analyze_resume
from interview_generator import generate_interview_questions

from speech_to_text import speech_to_text
from streamlit_mic_recorder import mic_recorder

# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="💼",
    layout="wide"
)


# -----------------------------
# Title
# -----------------------------

st.title("💼 AI Career Assistant")

st.write(
    "Upload your Resume and Job Description to analyze your career profile using AI."
)


# -----------------------------
# Session State
# -----------------------------

if "chatbot" not in st.session_state:
    st.session_state.chatbot = None

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "interview" not in st.session_state:
    st.session_state.interview = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.header("📂 Upload Documents")

    st.info(
        """
Supported formats:

• PDF
• JPG
• PNG

Upload:

1. Resume
2. Job Description
"""
    )


# -----------------------------
# Upload Section
# -----------------------------

resume_file = st.file_uploader(
    "📄 Upload Resume",
    type=[
        "pdf",
        "png",
        "jpg",
        "jpeg"
    ]
)


job_file = st.file_uploader(
    "📄 Upload Job Description",
    type=[
        "pdf",
        "png",
        "jpg",
        "jpeg"
    ]
)



# -----------------------------
# Process Documents
# -----------------------------

if st.button("🚀 Analyze Documents"):


    if resume_file is None or job_file is None:

        st.warning(
            "Please upload both Resume and Job Description."
        )


    else:

        with st.spinner("Processing documents..."):


            # Save files

            resume_path = save_uploaded_file(
                resume_file
            )

            job_path = save_uploaded_file(
                job_file
            )


            # Extract text

            resume_text = extract_document_text(
                resume_path
            )


            job_text = extract_document_text(
                job_path
            )


            complete_text = (

                resume_text

                +

                "\n\n"

                +

                job_text

            )


            # Split text

            chunks = split_text(
                complete_text
            )


            # Embeddings

            embeddings = load_embedding_model()


            # Vector Database

            vector_store = create_vector_store(
                chunks,
                embeddings
            )


            # LLM

            llm = load_llm()


            # Chatbot

            chatbot = create_chatbot(
                llm,
                vector_store
            )


            st.session_state.chatbot = chatbot



        # Resume Analysis

        with st.spinner("Generating Resume Analysis..."):

            analysis = analyze_resume(
                chatbot
            )

            st.session_state.analysis = analysis



        # Interview Questions

        with st.spinner("Generating Interview Questions..."):

            interview = generate_interview_questions(
                chatbot
            )

            st.session_state.interview = interview



        st.success(
            "Documents processed successfully!"
        )



# -----------------------------
# Resume Analysis
# -----------------------------

if st.session_state.analysis:


    st.header("📊 Resume Analysis")


    st.write(
        st.session_state.analysis
    )



# -----------------------------
# Interview Questions
# -----------------------------

if st.session_state.interview:


    st.header(
        "🎯 Interview Questions"
    )


    st.write(
        st.session_state.interview
    )



# -----------------------------
# Voice Input
# -----------------------------



st.header("🎤 Voice Question")

audio = mic_recorder(

    start_prompt="🎙️ Start Recording",

    stop_prompt="⏹️ Stop Recording",

    key="voice"
)

if audio:

    with st.spinner("Transcribing..."):

        voice_text = speech_to_text(
            audio["bytes"]
        )

    st.success("Voice converted to text!")

    st.write("You asked:")

    st.write(voice_text)

    if st.session_state.chatbot:

        with st.spinner("Thinking..."):

            answer = st.session_state.chatbot.ask(
                voice_text
            )

        st.write(answer)

    text = speech_to_text(audio["bytes"])

    st.write("You said:")

    st.write(text)

    if st.session_state.chatbot:

        answer = st.session_state.chatbot.ask(text)

        st.write(answer)


    with st.spinner("Listening..."):

        voice_text = speech_to_text()


    if voice_text:

        st.write(
            "You asked:",
            voice_text
        )


        if st.session_state.chatbot:


            answer = st.session_state.chatbot.ask(
                voice_text
            )


            st.write(
                answer
            )



# -----------------------------
# Chat Section
# -----------------------------

st.header(
    "💬 Chat With Resume"
)


if st.session_state.chatbot:


    question = st.text_input(
        "Ask something about your Resume"
    )


    if st.button("Ask AI"):


        if question:


            with st.spinner("Thinking..."):


                answer = st.session_state.chatbot.ask(
                    question
                )


            st.session_state.messages.append(
                {
                    "user": question,
                    "ai": answer
                }
            )



    # Show History

    for chat in st.session_state.messages:


        st.markdown(
            "### 👤 You"
        )

        st.write(
            chat["user"]
        )


        st.markdown(
            "### 🤖 AI"
        )

        st.write(
            chat["ai"]
        )


else:


    st.info(
        "Upload documents and click Analyze Documents first."
    )