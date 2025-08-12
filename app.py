import streamlit as st
from dotenv import dotenv_values
from IPython.display import Markdown
from pydub import AudioSegment
import io
from io import BytesIO
from openai import OpenAI
from IPython.display import Audio
import ffmpeg
import os
import subprocess
import sys

#os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

# env = dotenv_values(".env")

# openai_client = OpenAI(api_key=env["OPENAI_API_KEY"])



st.title("Subtitles :blue[Generator] :tv:")

#with st.sidebar:
    
#button_audio = st.button("Generate audio from the uploaded video file")

    #button_extract = st.button("Save audio file on your drive")

    # st.radio(
    # "Choose language for subtitles",
    # ["Subtitles in Polish", "Subtitles in English", "Subtitles in Spanish"],
    # )


uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    video_bytes = uploaded_file.read()
    st.video(video_bytes)

    if st.button("Generate audio from the uploaded video file"):
        try:
            # Próba automatycznego rozpoznania formatu z rozszerzenia pliku
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            audio_segment = AudioSegment.from_file(BytesIO(video_bytes), format=file_extension)
            
            mp3_buffer = BytesIO()
            audio_segment.export(mp3_buffer, format="mp3")
            mp3_buffer.seek(0)

            # Zapisz w session_state
            st.session_state["mp3_audio"] = mp3_buffer.getvalue()

            st.audio(mp3_buffer, format="audio/mp3")
        except Exception as e:
            st.error(f"❌ An error occurred while processing the audio: {e}")

    if st.button("Save audio file on your disk"):
        if "mp3_audio" in st.session_state:
            with open("output_audio.mp3", "wb") as f:
                f.write(st.session_state["mp3_audio"])
            st.success("Audio saved as output_audio.mp3")
        else:
            st.warning("Please click first 'Generate audio from the uploaded video file'.")











    



