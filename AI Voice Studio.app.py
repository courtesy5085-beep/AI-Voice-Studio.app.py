import streamlit as st
import io
import time
import zipfile
from datetime import datetime

from gtts import gTTS
import speech_recognition as sr
from langdetect import detect
from deep_translator import GoogleTranslator
from pypdf import PdfReader
from docx import Document
from pydub import AudioSegment
import edge_tts
import asyncio

# ================= CONFIG =================
st.set_page_config(page_title="AI Voice Studio", layout="wide")

# ================= SESSION =================
if "history" not in st.session_state:
    st.session_state.history = []

def add_history(action):
    st.session_state.history.append({
        "time": datetime.now().strftime("%H:%M"),
        "action": action
    })
    if len(st.session_state.history) > 50:
        st.session_state.history.pop(0)

# ================= HELPERS =================
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

# ================= EDGE TTS =================
async def edge_generate(text):
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
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
            st.error("TTS failed")
            return None

# ================= STT =================
def speech_to_text(file):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(file) as source:
            audio = r.record(source)
        return r.recognize_google(audio)
    except:
        return "Speech recognition failed"

# ================= FILE READER =================
def read_file(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        return " ".join([p.extract_text() or "" for p in reader.pages])
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return " ".join([p.text for p in doc.paragraphs])
    else:
        return file.read().decode("utf-8", errors="ignore")

# ================= SUBTITLE =================
def generate_srt(text):
    lines = text.split(".")
    srt = ""
    for i, line in enumerate(lines):
        srt += f"{i+1}\n00:00:{i:02d},000 --> 00:00:{i+2:02d},000\n{line.strip()}\n\n"
    return srt

# ================= UI =================
st.title("🎙️ AI Voice Studio")

tabs = st.tabs([
    "TTS",
    "STT",
    "Batch",
    "Subtitle",
    "History"
])

# ================= TTS =================
with tabs[0]:
    st.subheader("Text → Speech")

    text = st.text_area("Enter text")
    lang = st.selectbox("Language", list(LANGUAGES.keys()))

    if st.button("Generate"):
        if text:
            audio = tts_generate(text, LANGUAGES[lang])
            if audio:
                st.audio(audio)
                st.download_button("Download", audio, "audio.mp3")
                add_history("TTS")

# ================= STT =================
with tabs[1]:
    st.subheader("Speech → Text")

    file = st.file_uploader("Upload audio", type=["wav"])

    if file and st.button("Transcribe"):
        result = speech_to_text(file)
        st.text_area("Result", result)
        add_history("STT")

# ================= BATCH =================
with tabs[2]:
    st.subheader("Batch Converter")

    files = st.file_uploader("Upload multiple", accept_multiple_files=True)

    if files and st.button("Process"):
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as z:
            for f in files:
                text = read_file(f)
                audio = tts_generate(text[:2000], "en")
                if audio:
                    z.writestr(f.name + ".mp3", audio.read())

        st.download_button("Download ZIP", zip_buffer.getvalue(), "batch.zip")

# ================= SUBTITLE =================
with tabs[3]:
    st.subheader("Subtitle Generator")

    text = st.text_area("Paste text")

    if st.button("Generate SRT"):
        srt = generate_srt(text)
        st.download_button("Download", srt, "subtitles.srt")

# ================= HISTORY =================
with tabs[4]:
    st.subheader("History")

    for h in st.session_state.history[::-1]:
        st.write(h)
