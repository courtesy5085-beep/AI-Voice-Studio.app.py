"""
AI Voice Studio
================
A Streamlit application that showcases a suite of AI-powered voice and
document tools: text-to-speech playground, voice-to-text transcription,
translation, file/video readers, text-to-PDF export, and a usage dashboard.

All AI/ML calls are stubbed out with clearly-labeled placeholder functions so
the app runs end-to-end with zero API keys. Swap the placeholders for real
provider calls (OpenAI, Whisper, ElevenLabs, gTTS, etc.) when ready.
"""

import io
import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Voice Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for a clean, modern look
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Overall font */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        }

        /* Main title */
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .main-subtitle {
            color: #8a8a8a;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        /* Card container */
        .card {
            background-color: #ffffff10;
            border: 1px solid #ffffff22;
            border-radius: 14px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1rem;
        }

        /* Buttons */
        div.stButton > button {
            border-radius: 10px;
            padding: 0.5rem 1.2rem;
            font-weight: 600;
            border: none;
            background: linear-gradient(90deg, #7b2ff7, #f107a3);
            color: white;
            transition: 0.2s ease-in-out;
        }
        div.stButton > button:hover {
            opacity: 0.85;
            transform: translateY(-1px);
        }

        /* Sidebar radio spacing */
        section[data-testid="stSidebar"] .stRadio > label {
            font-size: 1rem;
        }

        /* Metric cards */
        div[data-testid="stMetric"] {
            background-color: #ffffff10;
            border: 1px solid #ffffff22;
            border-radius: 12px;
            padding: 0.8rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
def init_session_state():
    """Initialize all session_state keys used across pages."""
    defaults = {
        "generated_audio": None,
        "transcript": "",
        "translated_text": "",
        "extracted_text": "",
        "video_transcript": "",
        "pdf_bytes": None,
        "usage_log": {
            "Playground": 12,
            "Voice to Text": 8,
            "Translator": 15,
            "File Reader": 6,
            "Video Reader": 4,
            "Text to PDF": 9,
        },
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()

# ---------------------------------------------------------------------------
# Placeholder / stub AI functions
# ---------------------------------------------------------------------------
def generate_speech(text: str, voice: str) -> bytes:
    """
    Generate speech audio from text.

    # TODO: Plug in a real TTS provider here (e.g. ElevenLabs, gTTS, OpenAI TTS).
    Returns dummy silent WAV bytes so st.audio has something valid to play.
    """
    if not text.strip():
        raise ValueError("Text cannot be empty.")
    # Minimal valid WAV header for a near-silent clip (dummy placeholder audio)
    dummy_wav = (
        b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
        b"\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    )
    return dummy_wav


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe audio bytes into text.

    # TODO: Plug in Whisper API here (openai.Audio.transcriptions.create).
    """
    if not audio_bytes:
        return ""
    return "This is a placeholder transcript generated from your audio input."


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text from source_lang to target_lang.

    # TODO: Plug in a real translation API here (e.g. Google Translate, DeepL, OpenAI).
    """
    if not text.strip():
        return ""
    return f"[{target_lang} translation placeholder] {text}"


def extract_text_from_file(uploaded_file) -> str:
    """
    Extract text from an uploaded PDF, DOCX, or TXT file.
    """
    try:
        file_type = uploaded_file.name.split(".")[-1].lower()

        if file_type == "pdf":
            import PyPDF2

            reader = PyPDF2.PdfReader(uploaded_file)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text.strip() or "No extractable text found in this PDF."

        elif file_type == "docx":
            import docx

            document = docx.Document(uploaded_file)
            text = "\n".join(p.text for p in document.paragraphs)
            return text.strip() or "No extractable text found in this document."

        elif file_type == "txt":
            return uploaded_file.read().decode("utf-8", errors="ignore")

        else:
            return "Unsupported file type."

    except Exception as exc:
        raise RuntimeError(f"Failed to extract text: {exc}")


def extract_audio_from_video(uploaded_video) -> bytes:
    """
    Extract the audio track from an uploaded video file using moviepy.

    # TODO: In production, save uploaded_video to a temp file, run
    # moviepy.editor.VideoFileClip(path).audio.write_audiofile(...), then
    # feed the resulting audio into transcribe_audio().
    """
    if uploaded_video is None:
        return b""
    # Placeholder: pretend we extracted audio successfully
    return b"dummy_audio_bytes"


def text_to_pdf_bytes(text: str) -> bytes:
    """
    Convert plain text into a PDF file and return the bytes.
    """
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line)

    # fpdf2 returns a bytearray with dest="S"
    pdf_output = pdf.output(dest="S")
    if isinstance(pdf_output, str):
        pdf_output = pdf_output.encode("latin-1")
    return bytes(pdf_output)


def log_feature_usage(feature_name: str):
    """Increment the dummy usage counter for the dashboard."""
    if feature_name in st.session_state.usage_log:
        st.session_state.usage_log[feature_name] += 1


# ---------------------------------------------------------------------------
# Page: Playground
# ---------------------------------------------------------------------------
def playground():
    st.markdown('<div class="main-title">🎙️ Playground</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Turn text into natural-sounding speech.</div>',
        unsafe_allow_html=True,
    )

    with st.container():
        text_input = st.text_area(
            "Enter text to convert to speech",
            height=150,
            placeholder="Type or paste the text you'd like to hear spoken aloud...",
        )
        voice = st.selectbox(
            "Choose a voice",
            ["Aria (Female, US)", "Adam (Male, US)", "Nova (Female, UK)", "Leo (Male, AU)"],
        )

        if st.button("🎧 Generate Speech"):
            try:
                with st.spinner("Generating speech..."):
                    time.sleep(1)
                    st.session_state.generated_audio = generate_speech(text_input, voice)
                log_feature_usage("Playground")
                st.success("Speech generated successfully!")
            except ValueError as exc:
                st.error(f"⚠️ {exc}")

        if st.session_state.generated_audio:
            st.audio(st.session_state.generated_audio, format="audio/wav")
            st.download_button(
                "⬇️ Download Audio",
                data=st.session_state.generated_audio,
                file_name="generated_speech.wav",
                mime="audio/wav",
            )


# ---------------------------------------------------------------------------
# Page: Voice to Text
# ---------------------------------------------------------------------------
def voice_to_text():
    st.markdown('<div class="main-title">🎧 Voice to Text</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Record or upload audio and get an instant transcript.</div>',
        unsafe_allow_html=True,
    )

    tab_record, tab_upload = st.tabs(["🎙️ Record", "📁 Upload"])

    with tab_record:
        try:
            from streamlit_mic_recorder import mic_recorder

            audio = mic_recorder(
                start_prompt="Start Recording",
                stop_prompt="Stop Recording",
                just_once=False,
                key="mic_recorder",
            )
            if audio:
                st.audio(audio["bytes"])
                if st.button("Transcribe Recording"):
                    with st.spinner("Transcribing..."):
                        time.sleep(1)
                        st.session_state.transcript = transcribe_audio(audio["bytes"])
                    log_feature_usage("Voice to Text")
        except ImportError:
            st.warning(
                "The `streamlit-mic-recorder` package is not installed. "
                "Run `pip install streamlit-mic-recorder` to enable live recording."
            )

    with tab_upload:
        uploaded_audio = st.file_uploader(
            "Upload an audio file", type=["wav", "mp3", "m4a", "ogg"], key="audio_upload"
        )
        if uploaded_audio is not None:
            st.audio(uploaded_audio)
            if st.button("Transcribe Upload"):
                try:
                    with st.spinner("Transcribing..."):
                        time.sleep(1)
                        st.session_state.transcript = transcribe_audio(uploaded_audio.read())
                    log_feature_usage("Voice to Text")
                except Exception as exc:
                    st.error(f"⚠️ Transcription failed: {exc}")

    if st.session_state.transcript:
        st.text_area("Transcript", st.session_state.transcript, height=150)
        st.download_button(
            "⬇️ Download Transcript",
            data=st.session_state.transcript,
            file_name="transcript.txt",
            mime="text/plain",
        )


# ---------------------------------------------------------------------------
# Page: Translator
# ---------------------------------------------------------------------------
def translator():
    st.markdown('<div class="main-title">🌍 Translator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Translate text between languages and listen to the result.</div>',
        unsafe_allow_html=True,
    )

    languages = ["English", "Spanish", "French", "German", "Arabic", "Chinese", "Hindi", "Urdu"]

    text_input = st.text_area("Enter text to translate", height=140)
    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox("Source language", languages, index=0)
    with col2:
        target_lang = st.selectbox("Target language", languages, index=1)

    if st.button("🔄 Translate"):
        try:
            with st.spinner("Translating..."):
                time.sleep(1)
                st.session_state.translated_text = translate_text(
                    text_input, source_lang, target_lang
                )
            log_feature_usage("Translator")
        except Exception as exc:
            st.error(f"⚠️ Translation failed: {exc}")

    if st.session_state.translated_text:
        st.text_area("Translated text", st.session_state.translated_text, height=140)
        if st.button("🔊 Play Audio"):
            with st.spinner("Synthesizing audio..."):
                audio_bytes = generate_speech(st.session_state.translated_text, target_lang)
            st.audio(audio_bytes, format="audio/wav")


# ---------------------------------------------------------------------------
# Page: File Reader
# ---------------------------------------------------------------------------
def file_reader():
    st.markdown('<div class="main-title">📄 File Reader</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Upload a document and have it read aloud.</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader("Upload a PDF, DOCX, or TXT file", type=["pdf", "docx", "txt"])

    if uploaded_file is not None:
        try:
            with st.spinner("Extracting text..."):
                st.session_state.extracted_text = extract_text_from_file(uploaded_file)
            log_feature_usage("File Reader")
        except RuntimeError as exc:
            st.error(f"⚠️ {exc}")

    if st.session_state.extracted_text:
        st.text_area("Extracted text", st.session_state.extracted_text, height=250)
        if st.button("🔊 Read Aloud"):
            with st.spinner("Generating narration..."):
                audio_bytes = generate_speech(st.session_state.extracted_text, "Aria (Female, US)")
            st.audio(audio_bytes, format="audio/wav")


# ---------------------------------------------------------------------------
# Page: Video Reader
# ---------------------------------------------------------------------------
def video_reader():
    st.markdown('<div class="main-title">🎬 Video Reader</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Extract and transcribe audio from a video file.</div>',
        unsafe_allow_html=True,
    )

    uploaded_video = st.file_uploader("Upload an MP4 video", type=["mp4"])

    if uploaded_video is not None:
        st.video(uploaded_video)

        if st.button("Extract & Transcribe"):
            try:
                with st.spinner("Extracting audio from video..."):
                    audio_bytes = extract_audio_from_video(uploaded_video)
                    time.sleep(1)

                with st.spinner("Transcribing..."):
                    time.sleep(1)
                    st.session_state.video_transcript = transcribe_audio(audio_bytes)

                log_feature_usage("Video Reader")
                st.success("Transcription complete!")
            except Exception as exc:
                st.error(f"⚠️ Failed to process video: {exc}")

    if st.session_state.video_transcript:
        st.text_area("Video transcript", st.session_state.video_transcript, height=180)
        st.download_button(
            "⬇️ Download Transcript",
            data=st.session_state.video_transcript,
            file_name="video_transcript.txt",
            mime="text/plain",
        )


# ---------------------------------------------------------------------------
# Page: Text to PDF
# ---------------------------------------------------------------------------
def text_to_pdf():
    st.markdown('<div class="main-title">📝 Text to PDF</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Turn any block of text into a downloadable PDF.</div>',
        unsafe_allow_html=True,
    )

    text_input = st.text_area("Enter the text you want in your PDF", height=250)

    if st.button("📄 Download PDF"):
        if not text_input.strip():
            st.error("⚠️ Please enter some text before generating a PDF.")
        else:
            try:
                with st.spinner("Building PDF..."):
                    st.session_state.pdf_bytes = text_to_pdf_bytes(text_input)
                log_feature_usage("Text to PDF")
            except Exception as exc:
                st.error(f"⚠️ Failed to generate PDF: {exc}")

    if st.session_state.pdf_bytes:
        st.download_button(
            "⬇️ Download PDF",
            data=st.session_state.pdf_bytes,
            file_name=f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
        )


# ---------------------------------------------------------------------------
# Page: Dashboard
# ---------------------------------------------------------------------------
def dashboard():
    st.markdown('<div class="main-title">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">A quick snapshot of app usage and activity.</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sessions", "1,284", "+8.2%")
    col2.metric("Minutes Transcribed", "5,932", "+12.4%")
    col3.metric("Languages Used", "9", "+2")

    st.markdown("---")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        usage_df = pd.DataFrame(
            {
                "Feature": list(st.session_state.usage_log.keys()),
                "Uses": list(st.session_state.usage_log.values()),
            }
        )
        fig_bar = px.bar(
            usage_df,
            x="Feature",
            y="Uses",
            title="Feature Usage",
            color="Feature",
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with chart_col2:
        lang_df = pd.DataFrame(
            {
                "Language": ["English", "Spanish", "French", "Arabic", "Chinese"],
                "Sessions": [420, 210, 180, 150, 90],
            }
        )
        fig_pie = px.pie(
            lang_df,
            names="Language",
            values="Sessions",
            title="Languages",
            hole=0.4,
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
PAGES = {
    "🎙️ Playground": playground,
    "🎧 Voice to Text": voice_to_text,
    "🌍 Translator": translator,
    "📄 File Reader": file_reader,
    "🎬 Video Reader": video_reader,
    "📝 Text to PDF": text_to_pdf,
    "📊 Dashboard": dashboard,
}


def main():
    """App entry point: renders the sidebar and routes to the selected page."""
    st.sidebar.markdown("## 🎙️ AI Voice Studio")
    st.sidebar.caption("Your all-in-one AI voice & document toolkit")
    st.sidebar.markdown("---")

    selection = st.sidebar.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")

    st.sidebar.markdown("---")
    st.sidebar.caption("Built with Streamlit · Placeholder AI backends")

    page_function = PAGES[selection]
    page_function()


if __name__ == "__main__":
    main()
