"""Interview Prep: AI questions, dataset question bank, practice with AI feedback."""
import re

import streamlit as st

import theme
from core import ask_ai, docs_ready
from data_loader import get_fusion


def _parse_questions(text) -> list[str]:
    qs = []
    for line in str(text or "").splitlines():
        line = re.sub(r"^\s*(\d+[\.\)]|[-*•])\s*", "", line).strip(" *")
        if line.endswith("?") and len(line) > 15:
            qs.append(line)
    return qs


def render():
    theme.page_header("Interview Prep", "Generated questions, a role-based question bank and AI-scored practice.", "🎯")
    df = get_fusion()
    t1, t2, t3 = st.tabs(["🤖 Your AI questions", "📚 Question bank", "🎤 Practice mode"])

    with t1:
        if st.session_state.interview:
            st.write(st.session_state.interview)
            st.download_button("⬇️ Download questions", str(st.session_state.interview), "interview_questions.txt")
        else:
            st.info("📤 Upload documents in **Upload & Analyze** to get questions tailored to your resume.")

    with t2:
        role = st.selectbox("Role", sorted(df.job_title.unique()))
        sub = df[df.job_title == role]
        qs = sub.generated_interview_question.value_counts()
        st.caption(f"{len(qs)} unique questions generated for **{role}** across {len(sub)} records.")
        for q in qs.index[:25]:
            st.markdown(f"- {q}")
        top_missing = (sub.missing_skills.str.split(", ").explode().replace("", None).dropna()
                       .value_counts().head(5).index.tolist())
        if top_missing:
            theme.insight("Skills candidates most often lack for this role: "
                          + ", ".join(f"<b>{s}</b>" for s in top_missing))

    with t3:
        pool = _parse_questions(st.session_state.interview)
        source = "your AI questions" if pool else "the question bank"
        if not pool:
            pool = df.generated_interview_question.drop_duplicates().head(40).tolist()
        question = st.selectbox(f"Pick a question (from {source})", pool)
        answer = st.text_area("Your answer", height=160, placeholder="Type your answer as you would say it in the interview...")
        if st.button("Get AI feedback", type="primary"):
            if not answer.strip():
                st.warning("Write an answer first.")
            elif not docs_ready():
                st.info("📤 Upload documents first so the AI can use your resume for feedback.")
            else:
                prompt = (f"Act as an interviewer. Question: {question}\nCandidate answer: {answer}\n"
                          "Give a score out of 10, 2 strengths, 2 improvements, and a stronger sample answer "
                          "that uses details from the candidate's resume.")
                with st.spinner("Evaluating..."):
                    st.write(ask_ai(prompt, use_context=False))
