"""AI Career Assistant: multi-page app. Run with:  streamlit run app.py"""
import streamlit as st

st.set_page_config(page_title="AI Career Assistant", page_icon="💼", layout="wide")

import theme
from core import init_state, reset_state
from views import analyze, chat, dashboard, explorer, interview, jobs, market, report, skills, voice

theme.inject_css()
init_state()

PAGES = {
    "📊 Dashboard": dashboard.render,
    "📤 Upload & Analyze": analyze.render,
    "📝 Resume Report": report.render,
    "🎯 Interview Prep": interview.render,
    "💬 Chat With Resume": chat.render,
    "🎤 Voice Assistant": voice.render,
    "💼 Job Recommendations": jobs.render,
    "🧠 Skills Lab": skills.render,
    "💰 Salary & Market": market.render,
    "🔗 Data Explorer": explorer.render,
}

with st.sidebar:
    st.markdown("## 💼 AI Career Assistant")
    page = st.selectbox("Go to", list(PAGES), label_visibility="collapsed")
    st.divider()
    ss = st.session_state
    st.markdown("**Session**")
    st.markdown(
        theme.pill("Resume", bool(ss.resume_name)) + theme.pill("Job description", bool(ss.job_name))
        + theme.pill("Analysis", bool(ss.analysis)) + theme.pill("Interview Qs", bool(ss.interview)),
        unsafe_allow_html=True,
    )
    if ss.resume_name:
        st.caption(f"{ss.resume_name} · {ss.job_name}")
    st.caption(f"💬 {len(ss.messages)} chat messages")
    if st.button("♻️ Reset session"):
        reset_state()
        st.rerun()

PAGES[page]()
