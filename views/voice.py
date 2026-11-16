"""Voice Assistant."""
import streamlit as st

import theme
from core import ask_ai, require_docs


def render():
    theme.page_header("Voice Assistant", "Speak your question; it is transcribed and answered from your resume.", "🎤")
    if not require_docs():
        return
    from streamlit_mic_recorder import mic_recorder

    from speech_to_text import speech_to_text

    audio = mic_recorder(start_prompt="🎙️ Start recording", stop_prompt="⏹️ Stop recording", key="voice")
    ss = st.session_state

    # process each recording once (not on every rerun)
    if audio and audio.get("id") != ss.voice_last_id:
        ss.voice_last_id = audio.get("id")
        with st.spinner("Converting speech to text..."):
            text = speech_to_text(audio["bytes"])
        if text:
            with st.spinner("Searching resume & analysis..."):
                answer = ask_ai(text)
            ss.voice_history.append({"user": text, "ai": answer})
            ss.messages.append({"user": text, "ai": answer})
        else:
            st.warning("Could not understand the audio. Please try again.")

    if ss.voice_history:
        latest = ss.voice_history[-1]
        st.success("Voice recognized!")
        st.markdown("##### 🗣️ You asked")
        st.write(latest["user"])
        st.markdown("##### 🤖 AI Career Assistant")
        st.write(latest["ai"])
        if len(ss.voice_history) > 1:
            with st.expander(f"Earlier voice questions ({len(ss.voice_history) - 1})"):
                for h in reversed(ss.voice_history[:-1]):
                    st.markdown(f"**🗣️ {h['user']}**")
                    st.write(h["ai"])
                    st.divider()
    else:
        st.info("Press the microphone, ask your question, then press stop.")
