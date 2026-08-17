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
    type=["pdf", "png", "jpg", "jpeg"]
)

job_file = st.file_uploader(
    "📄 Upload Job Description",
    type=["pdf", "png", "jpg", "jpeg"]
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


            # Combine documents

            complete_text = (
                resume_text
                + "\n\n"
                + job_text
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


            # Create chatbot

            chatbot = create_chatbot(
                llm,
                vector_store
            )


            st.session_state.chatbot = chatbot


        # -----------------------------
        # Resume Analysis
        # -----------------------------

        with st.spinner(
            "Generating Resume Analysis..."
        ):

            analysis = analyze_resume(
                chatbot
            )

            st.session_state.analysis = analysis

            chatbot.analysis = analysis


        # -----------------------------
        # Interview Questions
        # -----------------------------

        with st.spinner(
            "Generating Interview Questions..."
        ):

            interview = generate_interview_questions(
                chatbot
            )

            st.session_state.interview = interview

            chatbot.interview = interview


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

    st.header("🎯 Interview Questions")

    st.write(
        st.session_state.interview
    )


# ============================================================
# VOICE INPUT
# ============================================================

st.header("🎤 Voice Question")

audio = mic_recorder(
    start_prompt="🎙️ Start Recording",
    stop_prompt="⏹️ Stop Recording",
    key="voice"
)


if audio:

    with st.spinner(
        "Converting speech to text..."
    ):

        voice_text = speech_to_text(
            audio["bytes"]
        )


    if voice_text:

        st.success("Voice recognized!")

        st.write("### 🗣️ You asked:")
        st.write(voice_text)


        if st.session_state.chatbot:

            with st.spinner(
                "Searching Resume & Analysis..."
            ):

                # Add analysis and interview information
                # to the voice question

                extra_context = ""

                if st.session_state.analysis:

                    extra_context += (
                        "\n\nRESUME ANALYSIS:\n"
                        + st.session_state.analysis
                    )

                if st.session_state.interview:

                    extra_context += (
                        "\n\nINTERVIEW QUESTIONS:\n"
                        + st.session_state.interview
                    )


                combined_question = (
                    voice_text
                    + extra_context
                )


                answer = st.session_state.chatbot.ask(
                    combined_question
                )


            st.write(
                "### 🤖 AI Career Assistant"
            )

            st.write(answer)


            st.session_state.messages.append(
                {
                    "user": voice_text,
                    "ai": answer
                }
            )

        else:

            st.warning(
                "Please upload documents and click Analyze Documents first."
            )

    else:

        st.warning(
            "Could not understand the audio. Please try again."
        )


# ============================================================
# CHAT SECTION
# ============================================================

st.header("💬 Chat With Resume")


if st.session_state.chatbot:

    question = st.text_input(
        "Ask something about your Resume"
    )


    if st.button("Ask AI"):

        if question:

            with st.spinner(
                "Thinking..."
            ):

                # Include generated analysis in the
                # chatbot's available information

                extra_context = ""


                if st.session_state.analysis:

                    extra_context += (
                        "\n\nRESUME ANALYSIS:\n"
                        + st.session_state.analysis
                    )


                if st.session_state.interview:

                    extra_context += (
                        "\n\nINTERVIEW QUESTIONS:\n"
                        + st.session_state.interview
                    )


                combined_question = (
                    question
                    + extra_context
                )


                answer = st.session_state.chatbot.ask(
                    combined_question
                )


            st.session_state.messages.append(
                {
                    "user": question,
                    "ai": answer
                }
            )


    # -----------------------------
    # Chat History
    # -----------------------------

    for chat in st.session_state.messages:

        st.markdown("### 👤 You")

        st.write(
            chat["user"]
        )

        st.markdown("### 🤖 AI")

        st.write(
            chat["ai"]
        )


else:

    st.info(
        "Upload documents and click Analyze Documents first."
    )