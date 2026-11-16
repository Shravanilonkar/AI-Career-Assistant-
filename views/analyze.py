
"""Upload & Analyze page."""

import time
import streamlit as st

import theme
from core import docs_ready


def run_step(name, function, *args):
    start = time.time()
    st.write(f"⏳ {name} started...")

    result = function(*args)

    elapsed = time.time() - start
    st.write(f"✅ {name} completed in {elapsed:.2f} seconds")

    return result


def render():

    theme.page_header(
        "Upload & Analyze",
        "Upload your resume and a job description to start.",
        "📤"
    )

    c1, c2 = st.columns(2)

    with c1:
        resume_file = st.file_uploader(
            "📄 Resume",
            type=["pdf", "png", "jpg", "jpeg"],
            key="up_resume"
        )

    with c2:
        job_file = st.file_uploader(
            "📄 Job description",
            type=["pdf", "png", "jpg", "jpeg"],
            key="up_job"
        )

    if docs_ready():
        st.success(
            f"Ready: **{st.session_state.resume_name}** "
            f"vs **{st.session_state.job_name}**. "
            "Open the other pages from the sidebar."
        )

    if st.button("🚀 Analyze Documents", type="primary"):

        if resume_file is None or job_file is None:
            st.warning("Please upload both Resume and Job Description.")
            return

        from chatbot import create_chatbot
        from document_processor import extract_document_text
        from embeddings import load_embedding_model
        from file_handler import save_uploaded_file
        from interview_generator import generate_interview_questions
        from llm import load_llm
        from resume_analyzer import analyze_resume
        from text_splitter import split_text
        from vector_store import create_vector_store

        try:

            with st.status(
                "Processing documents...",
                expanded=True
            ) as status:

                resume_path = run_step(
                    "Saving resume",
                    save_uploaded_file,
                    resume_file
                )

                job_path = run_step(
                    "Saving job description",
                    save_uploaded_file,
                    job_file
                )

                resume_text = run_step(
                    "Extracting resume text",
                    extract_document_text,
                    resume_path
                )

                job_text = run_step(
                    "Extracting job description text",
                    extract_document_text,
                    job_path
                )

                st.write(f"Resume characters: {len(resume_text)}")
                st.write(f"Job description characters: {len(job_text)}")

                chunks = run_step(
                    "Splitting documents",
                    split_text,
                    resume_text + "\n\n" + job_text
                )

                st.write(f"Total chunks: {len(chunks)}")

                embedding_model = run_step(
                    "Loading embedding model",
                    load_embedding_model
                )

                vector_store = run_step(
                    "Creating FAISS database",
                    create_vector_store,
                    chunks,
                    embedding_model
                )

                llm = run_step(
                    "Loading Groq model",
                    load_llm
                )

                chatbot = create_chatbot(llm, vector_store)

                analysis = run_step(
                    "Generating resume analysis",
                    analyze_resume,
                    chatbot,
                    resume_text,
                    job_text
                )

                chatbot.analysis = analysis

                interview = run_step(
                    "Generating interview questions",
                    generate_interview_questions,
                    chatbot
                )

                chatbot.interview = interview

                ss = st.session_state

                ss.chatbot = chatbot
                ss.analysis = analysis
                ss.interview = interview

                ss.resume_text = str(resume_text or "")
                ss.job_text = str(job_text or "")

                ss.resume_name = resume_file.name
                ss.job_name = job_file.name

                ss.messages = []

                status.update(
                    label="Documents processed successfully!",
                    state="complete"
                )

            st.rerun()

        except Exception as e:
            st.error(f"Processing failed: {type(e).__name__}: {e}")
            st.exception(e)

    if docs_ready():

        with st.expander("Preview extracted text"):

            t1, t2 = st.tabs(["Resume", "Job description"])

            t1.text(st.session_state.resume_text[:6000] or "(empty)")
            t2.text(st.session_state.job_text[:6000] or "(empty)")
