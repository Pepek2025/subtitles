import streamlit as st
from dotenv import dotenv_values
from IPython.display import Markdown
from pydub import AudioSegment
from io import BytesIO
from openai import OpenAI
from IPython.display import Audio
import ffmpeg
import os
import subprocess
import sys
from pathlib import Path

#Niezbędny do uruchomienia aplikacji lokalnej
#os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

env = dotenv_values(".env")

def get_openai_client():
    return OpenAI(api_key=st.session_state["openai_api_key"])

#
# MAIN
#

# Sprawdź czy mamy klucz API w session_state
if not st.session_state.get("openai_api_key"):
    if "OPENAI_API_KEY" in env:
        st.session_state["openai_api_key"] = env["OPENAI_API_KEY"]
    else:
        # jeśli brak → poproś użytkownika
        st.info("👉 Add your OpenAI API key to use this app")
        api_key_input = st.text_input("🔑 OpenAI API Key", type="password")
        if api_key_input:
            st.session_state["openai_api_key"] = api_key_input
            st.rerun()

if not st.session_state.get("openai_api_key"):
    st.stop()

openai_client = get_openai_client()

st.markdown(
    "<h1 style='text-align: center;'>Subtitles <span style='color: green;'>Generator</span> 🎬</h1>",
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("**Upload a video file**", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    video_bytes = uploaded_file.read()
    st.video(video_bytes)

    if st.button("**:large_blue_circle: Generate audio from the uploaded video file**"):
        try:
            # Próba automatycznego rozpoznania formatu z rozszerzenia pliku
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            audio_segment = AudioSegment.from_file(BytesIO(video_bytes), format=file_extension)
            
            mp3_buffer = BytesIO()
            audio_segment.export(mp3_buffer, format="mp3")
            mp3_buffer.seek(0)

            # Zapisz w session_state
            st.session_state["mp3_audio"] = mp3_buffer

        except Exception as e:
            st.error(f"❌ An error occurred while processing the audio: {e}")

    if "mp3_audio" in st.session_state:
        st.audio(st.session_state["mp3_audio"], format="audio/mp3")

    
    if "mp3_audio" in st.session_state:
        st.download_button(
            label="**💾 Download audio file to your disk**",
            data=st.session_state["mp3_audio"].getvalue(),
            file_name="output_audio.mp3",
            mime="audio/mpeg"
        )

    language_selection = st.radio("Select transcription language", options=[
        ("pl", "Polski 🇵🇱"),
        ("en", "English 🇬🇧"),
        ("es", "Español 🇪🇸")
        ],
        format_func=lambda x: x[1])[0]

    if st.button("**:large_blue_circle: Transcription from audio**"):
        if "mp3_audio" in st.session_state:
            # MP3 audio z session_state (BytesIO)
            mp3_audio = st.session_state["mp3_audio"]
            mp3_audio.seek(0)
            transcript = openai_client.audio.transcriptions.create(
                file=("audio.mp3", mp3_audio, "audio/mpeg"),
                model="whisper-1",
                response_format="srt",
                language=language_selection
            )
            # Zapisz w session_state
            st.session_state["subtitles_srt"] = transcript
            
    if "subtitles_srt" in st.session_state:
        edited_subtitles = st.text_area(
        "Subtitle file content ready for editing:",
        st.session_state["subtitles_srt"],
        height=400,
        key="subtitles_editor"
        )
           
        st.session_state["subtitles_srt"] = edited_subtitles

    if "subtitles_srt" in st.session_state:
        st.download_button(
            label="**💾 Download subtitles file on your disk**",
            data=st.session_state["subtitles_srt"],
            file_name="subtitles.srt",
            mime="text/plain"
        )
    else:
        st.error("No subtitles found. Please generate them first.")


if "subtitles_srt" in st.session_state and uploaded_file is not None:
    if st.button("**:large_blue_circle: Embed subtitles into video**"):
        # Save uploaded video to a temp path
        temp_video_path = Path("temp_video.mp4")
        temp_video_path.write_bytes(uploaded_file.getbuffer())  # safer than .read()

        # Save subtitles to temp path
        temp_srt_path = Path("temp_subtitles.srt")
        temp_srt_path.write_text(st.session_state["subtitles_srt"], encoding="utf-8")

        output_path = Path("video_with_subs.mp4")

        # FFmpeg command
        command = [
            "ffmpeg",
            "-i", str(temp_video_path),
            "-vf", f"subtitles='{temp_srt_path}'",
            "-c:a", "copy",
            str(output_path)
        ]

        try:
            subprocess.run(command, check=True)

            with open(output_path, "rb") as f:
                st.session_state["video_with_subs"] = f.read()
            
            st.success("Subtitles embedded successfully!")
        
        except subprocess.CalledProcessError as e:
            st.error(f"FFmpeg error: {e}")

        
         
    if "video_with_subs" in st.session_state:
        st.video(st.session_state["video_with_subs"])
        st.download_button(
            label="💾 Download video with subtitles",
            data=st.session_state["video_with_subs"],
            file_name="video_with_subs.mp4",
            mime="video/mp4"
        )









    



