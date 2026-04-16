# =========================
# AI VOICE STUDIO - SINGLE FILE SAAS APP
# =========================

import streamlit as st
import asyncio
import io
import time
import zipfile
import tempfile
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Core libs
from gtts import gTTS
import speech_recognition as sr
from langdetect import detect
from deep_translator import GoogleTranslator
from pypdf import PdfReader
from docx import Document
from pydub import AudioSegment

# Advanced TTS
import edge_tts

# Whisper fallback
import whisper

# Coqui TTS (Voice cloning)
from TTS.api import TTS

# UI
from streamlit_lottie import st_lottie
import requests

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI Voice Studio", layout="wide")

# =========================
# CACHE
# =========================
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

@st.cache_resource
def load_tts():
    return TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")

# =========================
# UI CSS (VFX)
# =========================
st.markdown("""
<style>
body {background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);}
.stButton>button {
    background: linear-gradient(45deg,#00c6ff,#0072ff);
    border-radius:12px;
    color:white;
}
.glass {
    background: rgba(255,255,255,0.08);
    padding:20px;
    border-radius:20px;
    backdrop-filter: blur(20px);
}
</style>
""", unsafe_allow_html=True)

# =========================
# HELPERS
# =========================
LANGUAGES = {
    "English": "en",
    "Urdu": "ur",
    "Hindi": "hi"
}

def detect_lang(text):
    try:
        return detect(text)
    except:
        return "en"

# =========================
# TTS ENGINE (EDGE → gTTS → fallback)
# =========================
async def edge_generate(text, voice="en-US-AriaNeural"):
    communicate = edge_tts.Communicate(text, voice)
    fp = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            fp.write(chunk["data"])
    fp.seek(0)
    return fp

def tts_generate(text, lang):
    try:
        return asyncio.run(edge_generate(text))
    except:
        try:
            tts = gTTS(text=text, lang=lang)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp
        except:
            return None

# =========================
# STT WITH WHISPER FALLBACK
# =========================
def speech_to_text(file):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(file) as source:
            audio = r.record(source)
        return r.recognize_google(audio)
    except:
        model = load_whisper()
        result = model.transcribe(file)
        return result["text"]

# =========================
# FILE READERS
# =========================
def read_file(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        return " ".join([p.extract_text() or "" for p in reader.pages])
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return " ".join([p.text for p in doc.paragraphs])
    else:
        return file.read().decode("utf-8", errors="ignore")

# =========================
# SUBTITLE GENERATOR
# =========================
def generate_srt(text):
    lines = text.split(".")
    srt = ""
    for i, line in enumerate(lines):
        srt += f"{i+1}\n00:00:{i:02d},000 --> 00:00:{i+2:02d},000\n{line.strip()}\n\n"
    return srt

# =========================
# PODCAST MIXER
# =========================
def podcast_mode(text, music_file):
    speech = tts_generate(text, "en")
    speech_audio = AudioSegment.from_file(speech, format="mp3")

    music = AudioSegment.from_file(music_file)
    music = music - 20

    combined = music.overlay(speech_audio)
    fp = io.BytesIO()
    combined.export(fp, format="mp3")
    fp.seek(0)
    return fp

# =========================
# VOICE CLONING
# =========================
def clone_voice(sample, text):
    tts = load_tts()
    output = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tts.tts_to_file(text=text, speaker_wav=sample, file_path=output.name)
    return open(output.name, "rb")

# =========================
# SESSION STATE
# =========================
if "history" not in st.session_state:
    st.session_state.history = []

def add_history(action):
    st.session_state.history.append({
        "time": datetime.now().strftime("%H:%M"),
        "action": action
    })
    if len(st.session_state.history) > 50:
        st.session_state.history.pop(0)

# =========================
# TABS
# =========================
tabs = st.tabs([
    "TTS",
    "STT",
    "Batch",
    "Podcast",
    "Clone",
    "Subtitle",
    "Analytics",
    "History"
])

# =========================
# TAB 1: TTS
# =========================
with tabs[0]:
    st.header("Text → Speech")

    text = st.text_area("Enter Text")
    lang = st.selectbox("Language", list(LANGUAGES.keys()))

    if st.button("Generate"):
        audio = tts_generate(text, LANGUAGES[lang])
        if audio:
            st.audio(audio)
            st.download_button("Download", audio, "audio.mp3")
            add_history("TTS")

# =========================
# TAB 2: STT
# =========================
with tabs[1]:
    st.header("Speech → Text")

    file = st.file_uploader("Upload audio")

    if file and st.button("Transcribe"):
        result = speech_to_text(file)
        st.text_area("Result", result)
        add_history("STT")

# =========================
# TAB 3: BATCH
# =========================
with tabs[2]:
    st.header("Batch Converter")

    files = st.file_uploader("Upload multiple", accept_multiple_files=True)

    if files and st.button("Process"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as z:
            for f in files:
                text = read_file(f)
                audio = tts_generate(text[:2000], "en")
                z.writestr(f.name + ".mp3", audio.read())

        st.download_button("Download ZIP", zip_buffer.getvalue(), "batch.zip")

# =========================
# TAB 4: PODCAST
# =========================
with tabs[3]:
    st.header("Podcast Studio")

    text = st.text_area("Script")
    music = st.file_uploader("Background Music")

    if text and music and st.button("Create Podcast"):
        audio = podcast_mode(text, music)
        st.audio(audio)

# =========================
# TAB 5: CLONE
# =========================
with tabs[4]:
    st.header("Voice Cloning")

    sample = st.file_uploader("Upload Voice Sample")
    text = st.text_input("Text")

    if sample and text and st.button("Clone"):
        audio = clone_voice(sample, text)
        st.audio(audio)

# =========================
# TAB 6: SUBTITLE
# =========================
with tabs[5]:
    st.header("Subtitle Generator")

    text = st.text_area("Paste Text")

    if st.button("Generate SRT"):
        srt = generate_srt(text)
        st.download_button("Download", srt, "subtitles.srt")

# =========================
# TAB 7: ANALYTICS
# =========================
with tabs[6]:
    st.header("Analytics")

    data = {}
    for h in st.session_state.history:
        data[h["action"]] = data.get(h["action"], 0) + 1

    st.bar_chart(data)

# =========================
# TAB 8: HISTORY
# =========================
with tabs[7]:
    st.header("History")

    for h in st.session_state.history[::-1]:
        st.write(h)
