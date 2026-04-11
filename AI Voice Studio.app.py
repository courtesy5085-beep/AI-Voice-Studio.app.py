import streamlit as st
from gtts import gTTS
import speech_recognition as sr
from langdetect import detect
from pypdf import PdfReader
from docx import Document
from pydub import AudioSegment
import tempfile
import io

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Voice Studio Pro",
    page_icon="🎧",
    layout="wide"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}
h1, h2, h3 {
    color: #22d3ee;
}
.stButton>button {
    background: linear-gradient(90deg,#06b6d4,#3b82f6);
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 16px;
}
.stTextArea textarea {
    border-radius: 10px;
}
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<h1 style='text-align: center;'>🎧 AI Voice Studio Pro</h1>
<p style='text-align: center;'>🚀 Convert Text ↔ Speech | Multi-language | File Reader</p>
""", unsafe_allow_html=True)

# ---------- HELPERS ----------

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

def text_to_speech(text, lang, slow=False):
    try:
        tts = gTTS(text=text, lang=lang, slow=slow)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except Exception as e:
        return None

def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except Exception as e:
        return f"Error: {str(e)}"

def read_pdf(file):
    text = ""
    reader = PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def read_docx(file):
    text = ""
    doc = Document(file)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def read_txt(file):
    return file.read().decode("utf-8")

# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(["🔊 Text to Speech", "🎤 Speech to Text", "📄 File Reader"])

# ---------- TAB 1 ----------
with tab1:
    st.subheader("📝 Text to Speech Converter")

    col1, col2 = st.columns([3,1])

    with col1:
        text_input = st.text_area("Enter your text", height=180)

    with col2:
        lang_option = st.selectbox(
            "Language",
            ["auto", "en", "ur", "hi", "ar", "fr", "de", "es"]
        )

        speed = st.radio("Voice Speed", ["Normal", "Slow"])

    st.caption(f"Characters: {len(text_input)}")

    if st.button("🎧 Generate Voice"):
        if text_input.strip() == "":
            st.warning("⚠️ Please enter text")
        else:
            with st.spinner("Generating AI Voice..."):
                lang = detect_language(text_input) if lang_option == "auto" else lang_option
                slow = True if speed == "Slow" else False

                audio = text_to_speech(text_input, lang, slow)

                if audio:
                    st.success(f"✅ Detected Language: {lang}")
                    st.audio(audio)

                    st.download_button(
                        "⬇️ Download MP3",
                        data=audio,
                        file_name="voice.mp3"
                    )
                else:
                    st.error("❌ Failed to generate audio")

# ---------- TAB 2 ----------
with tab2:
    st.subheader("🎤 Speech to Text AI")

    uploaded_audio = st.file_uploader("Upload Audio", type=["wav","mp3","ogg"])

    if uploaded_audio:
        st.audio(uploaded_audio)

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_audio.read())
            temp_path = tmp.name

        if not temp_path.endswith(".wav"):
            sound = AudioSegment.from_file(temp_path)
            temp_wav = temp_path + ".wav"
            sound.export(temp_wav, format="wav")
            temp_path = temp_wav

        if st.button("🧠 Convert Speech"):
            with st.spinner("Processing..."):
                text = speech_to_text(temp_path)
                st.text_area("Result:", text, height=150)

# ---------- TAB 3 ----------
with tab3:
    st.subheader("📄 File to Voice")

    uploaded_file = st.file_uploader("Upload PDF / DOCX / TXT", type=["pdf","docx","txt"])

    if uploaded_file:
        file_type = uploaded_file.name.split(".")[-1]

        with st.spinner("Reading file..."):
            if file_type == "pdf":
                content = read_pdf(uploaded_file)
            elif file_type == "docx":
                content = read_docx(uploaded_file)
            else:
                content = read_txt(uploaded_file)

        st.text_area("Preview", content[:2000], height=200)

        if st.button("🔊 Convert File"):
            with st.spinner("Generating voice..."):
                lang = detect_language(content)
                audio = text_to_speech(content[:3000], lang)

                if audio:
                    st.audio(audio)
                    st.download_button(
                        "⬇️ Download",
                        data=audio,
                        file_name="file_audio.mp3"
                    )
                else:
                    st.error("Error generating audio")
