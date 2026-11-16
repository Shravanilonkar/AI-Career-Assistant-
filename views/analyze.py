"""Upload & Analyze: your original pipeline, unchanged, on its own page."""
import streamlit as st

import theme
from core import docs_ready


def render():
    theme.page_header("Upload & Analyze", "Upload your resume and a job description to start.", "📤")

    c1, c2 = st.columns(2)
    with c1:
        resume_file = st.file_uploader("📄 Resume", type=["pdf", "png", "jpg", "jpeg"], key="up_resume")
    with c2:
        job_file = st.file_uploader("📄 Job description", type=["pdf", "png", "jpg", "jpeg"], key="up_job")

    if docs_ready():
        st.success(f"Ready: **{st.session_state.resume_name}** vs **{st.session_state.job_name}**. "
                   "Open the other pages from the sidebar.")

    if st.button("🚀 Analyze Documents", type="primary"):
        if resume_file is None or job_file is None:
            st.warning("Please upload both Resume and Job Description.")
            return

        # imported here so the dashboard still opens if a backend dependency is missing
        from chatbot import create_chatbot
        from document_processor import extract_document_text
        from embeddings import load_embedding_model
        from file_handler import save_uploaded_file
        from interview_generator import generate_interview_questions
        from llm import load_llm
        from resume_analyzer import analyze_resume
        from text_splitter import split_text
        from vector_store import create_vector_store

        with st.status("Processing documents...", expanded=True) as status:
            st.write("Reading files")
            resume_text = extract_document_text(save_uploaded_file(resume_file))
            job_text = extract_document_text(save_uploaded_file(job_file))

            st.write("Building search index")
            chunks = split_text(resume_text + "\n\n" + job_text)
            vector_store = create_vector_store(chunks, load_embedding_model())
            chatbot = create_chatbot(load_llm(), vector_store)

            st.write("Generating resume analysis")
            analysis = analyze_resume(chatbot, resume_text, job_text)
            chatbot.analysis = analysis

            st.write("Generating interview questions")
            interview = generate_interview_questions(chatbot)
            chatbot.interview = interview

            ss = st.session_state
            ss.chatbot, ss.analysis, ss.interview = chatbot, analysis, interview
            ss.resume_text, ss.job_text = str(resume_text or ""), str(job_text or "")
            ss.resume_name, ss.job_name = resume_file.name, job_file.name
            ss.messages = []
            status.update(label="Documents processed successfully!", state="complete")
        st.rerun()

    if docs_ready():
        with st.expander("Preview extracted text"):
            t1, t2 = st.tabs(["Resume", "Job description"])
            t1.text(st.session_state.resume_text[:6000] or "(empty)")
            t2.text(st.session_state.job_text[:6000] or "(empty)")
