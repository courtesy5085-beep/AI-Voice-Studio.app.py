import streamlit as st
import io, zipfile, asyncio, time, requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from gtts import gTTS
import speech_recognition as sr
from langdetect import detect
from deep_translator import GoogleTranslator
from pypdf import PdfReader
from docx import Document
from pydub import AudioSegment
import edge_tts

# ================= CONFIG =================
st.set_page_config(page_title="AI Voice Studio PRO", layout="wide")

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
    "Hindi": "hi",
    "Arabic": "ar"
}

def detect_lang(text):
    try:
        return detect(text)
    except:
        return "en"

# ================= SMART CHUNKING =================
def smart_chunks(text, max_len=500):
    sentences = text.split(".")
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) < max_len:
            current += s + "."
        else:
            chunks.append(current)
            current = s
    if current:
        chunks.append(current)
    return chunks

# ================= EDGE TTS =================
async def edge_generate(text, voice, rate):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    fp = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            fp.write(chunk["data"])
    fp.seek(0)
    return fp

def tts_generate(text, lang, speed):
    voice = "en-US-AriaNeural" if lang == "en" else "ur-PK-AsmaNeural"
    rate = f"+{int((speed-1)*100)}%" if speed >= 1 else f"{int((speed-1)*100)}%"
    try:
        return asyncio.run(edge_generate(text, voice, rate))
    except:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp

# ================= STT =================
def speech_to_text(file):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(file) as source:
            audio = r.record(source)
        return r.recognize_google(audio)
    except:
        return "STT failed"

# ================= FILE READ =================
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

# ================= PODCAST =================
def podcast_mode(text, music_file):
    speech = tts_generate(text, "en", 1.0)
    speech_audio = AudioSegment.from_file(speech, format="mp3")
    music = AudioSegment.from_file(music_file) - 20
    combined = music.overlay(speech_audio)
    fp = io.BytesIO()
    combined.export(fp, format="mp3")
    fp.seek(0)
    return fp

# ================= UI =================
st.title("🎙️ AI Voice Studio PRO")

tabs = st.tabs([
    "TTS PRO",
    "STT",
    "Batch",
    "Podcast",
    "Subtitle",
    "Analytics",
    "History"
])

# ================= TAB 1 =================
with tabs[0]:
    st.subheader("🔥 Advanced Text → Speech")

    text = st.text_area("Enter text")
    lang = st.selectbox("Language", list(LANGUAGES.keys()))
    speed = st.slider("Speed", 0.5, 3.0, 1.0)

    translate = st.toggle("Auto Translate")

    if st.button("Generate"):
        if text:
            if translate:
                text = GoogleTranslator(source='auto', target=LANGUAGES[lang]).translate(text)

            chunks = smart_chunks(text)
            final_audio = io.BytesIO()

            for c in chunks:
                audio = tts_generate(c, LANGUAGES[lang], speed)
                final_audio.write(audio.read())

            final_audio.seek(0)

            st.audio(final_audio)
            st.download_button("Download", final_audio, "audio.mp3")
            add_history("TTS")

# ================= TAB 2 =================
with tabs[1]:
    st.subheader("Speech → Text")

    file = st.file_uploader("Upload WAV", type=["wav"])

    if file and st.button("Transcribe"):
        result = speech_to_text(file)
        st.text_area("Result", result)
        add_history("STT")

# ================= TAB 3 =================
with tabs[2]:
    st.subheader("Batch Processing")

    files = st.file_uploader("Upload files", accept_multiple_files=True)

    if files and st.button("Process"):
        zip_buffer = io.BytesIO()
        progress = st.progress(0)

        with zipfile.ZipFile(zip_buffer, "w") as z:
            for i, f in enumerate(files):
                text = read_file(f)
                audio = tts_generate(text[:2000], "en", 1.0)
                z.writestr(f.name + ".mp3", audio.read())
                progress.progress((i+1)/len(files))

        st.download_button("Download ZIP", zip_buffer.getvalue(), "batch.zip")

# ================= TAB 4 =================
with tabs[3]:
    st.subheader("🎧 Podcast Mode")

    text = st.text_area("Podcast Script")
    music = st.file_uploader("Music")

    if text and music and st.button("Create"):
        audio = podcast_mode(text, music)
        st.audio(audio)

# ================= TAB 5 =================
with tabs[4]:
    st.subheader("Subtitle Generator")

    text = st.text_area("Paste text")

    if st.button("Generate SRT"):
        srt = generate_srt(text)
        st.download_button("Download", srt, "subtitles.srt")

# ================= TAB 6 =================
with tabs[5]:
    st.subheader("Analytics")

    data = {}
    for h in st.session_state.history:
        data[h["action"]] = data.get(h["action"], 0) + 1

    st.bar_chart(data)

# ================= TAB 7 =================
with tabs[6]:
    st.subheader("History")

    for h in st.session_state.history[::-1]:
        st.write(h)
