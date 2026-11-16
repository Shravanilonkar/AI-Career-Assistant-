"""Session state + the bridge to your existing chatbot."""
import streamlit as st

DEFAULTS = {
    "chatbot": None,
    "analysis": None,
    "interview": None,
    "messages": [],          # [{"user": ..., "ai": ...}]
    "resume_text": "",
    "job_text": "",
    "resume_name": "",
    "job_name": "",
    "voice_last_id": None,
    "voice_history": [],     # [{"user": ..., "ai": ...}]
    "jobs_df": None,
    "jobs_query": "",
}


def init_state():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = list(v) if isinstance(v, list) else v


def reset_state():
    for k, v in DEFAULTS.items():
        st.session_state[k] = list(v) if isinstance(v, list) else v


def docs_ready() -> bool:
    return st.session_state.chatbot is not None


def require_docs() -> bool:
    """Show a friendly nudge on pages that need the processed documents."""
    if docs_ready():
        return True
    st.info("📤 Upload your resume and job description in **Upload & Analyze** first.")
    return False


def ask_ai(question: str, use_context: bool = True, max_chars: int = 3500) -> str:
    """Same behaviour as your original app: question + analysis + interview context."""
    extra = ""
    if use_context:
        if st.session_state.analysis:
            extra += "\n\nRESUME ANALYSIS:\n" + str(st.session_state.analysis)[:max_chars]
        if st.session_state.interview:
            extra += "\n\nINTERVIEW QUESTIONS:\n" + str(st.session_state.interview)[:max_chars]
    return st.session_state.chatbot.ask(question + extra)
