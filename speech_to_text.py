import streamlit as st
import tempfile
import os

from groq import Groq


client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)


def speech_to_text(audio_bytes):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as temp_audio:

        temp_audio.write(audio_bytes)

        temp_path = temp_audio.name

    with open(temp_path, "rb") as audio_file:

        transcription = client.audio.transcriptions.create(

            file=audio_file,

            model="whisper-large-v3-turbo",

            response_format="json",

            temperature=0,

            language="en"
        )

    os.remove(temp_path)

    return transcription.text