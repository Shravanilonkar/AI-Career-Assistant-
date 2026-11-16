"""Chat With Resume."""
import streamlit as st

import theme
from core import ask_ai, require_docs

SUGGESTIONS = [
    "Summarize my profile in 3 lines",
    "What are my biggest skill gaps for this job?",
    "Rewrite my resume summary for this role",
    "Which projects should I highlight?",
]


def render():
    theme.page_header("Chat With Resume", "Ask anything about your resume and the target job.", "💬")
    if not require_docs():
        return
    msgs = st.session_state.messages

    top = st.columns([6, 1])
    top[0].markdown("".join(theme.pill(s) for s in ["RAG over resume + JD", "uses analysis as context"]),
                    unsafe_allow_html=True)
    if top[1].button("🗑️ Clear"):
        st.session_state.messages = []
        st.rerun()

    picked = None
    if not msgs:
        cols = st.columns(len(SUGGESTIONS))
        for c, s in zip(cols, SUGGESTIONS):
            if c.button(s, key=f"sug_{s}"):
                picked = s

    for m in msgs:
        with st.chat_message("user"):
            st.write(m["user"])
        with st.chat_message("assistant"):
            st.write(m["ai"])

    prompt = st.chat_input("Ask something about your resume") or picked
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_ai(prompt)
            st.write(answer)
        msgs.append({"user": prompt, "ai": answer})

    if msgs:
        transcript = "\n\n".join(f"You: {m['user']}\nAI: {m['ai']}" for m in msgs)
        st.download_button("⬇️ Download chat", transcript, "resume_chat.txt")
