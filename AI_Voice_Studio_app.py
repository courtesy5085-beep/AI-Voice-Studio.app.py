import streamlit as st
import io, os, zipfile, asyncio, tempfile
from datetime import datetime

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

# Google Speech Recognition locale codes (used for STT + Video Reader)
STT_LANGUAGES = {
    "English": "en-US",
    "Urdu": "ur-PK",
    "Hindi": "hi-IN",
    "Arabic": "ar-SA"
}

def detect_lang(text):
    try:
        return detect(text)
    except Exception:
        return "en"

# ================= SMART CHUNKING (text) =================
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
    except Exception:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp

# ================= AUDIO UTILITIES (shared by STT + Video Reader) =================
def load_audio_segment(uploaded_file):
    """Load any uploaded audio/video file into a pydub AudioSegment.
    Writes to a temp file first so ffmpeg can sniff the real container/codec
    (needed for video files and some audio formats)."""
    suffix = os.path.splitext(uploaded_file.name)[1] or ".dat"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    try:
        audio = AudioSegment.from_file(tmp_path)
    finally:
        os.remove(tmp_path)
    return audio

def transcribe_segment(segment, language="en-US"):
    """Transcribe a single pydub AudioSegment via SpeechRecognition."""
    r = sr.Recognizer()
    buf = io.BytesIO()
    segment.set_channels(1).export(buf, format="wav")
    buf.seek(0)
    with sr.AudioFile(buf) as source:
        audio_data = r.record(source)
    try:
        return r.recognize_google(audio_data, language=language)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"[STT service error: {e}]"

def transcribe_long_audio(audio, language="en-US", chunk_ms=30000, progress_cb=None):
    """Split audio into fixed-length chunks (Google's free STT endpoint chokes
    on long clips) and transcribe each, returning text + timestamp per chunk."""
    total = len(audio)
    n_chunks = max(1, (total + chunk_ms - 1) // chunk_ms)
    results, timestamps = [], []
    for i in range(n_chunks):
        start = i * chunk_ms
        end = min(start + chunk_ms, total)
        segment = audio[start:end]
        text = transcribe_segment(segment, language)
        results.append(text)
        timestamps.append((start, end))
        if progress_cb:
            progress_cb((i + 1) / n_chunks)
    return results, timestamps

def ms_to_srt_time(ms):
    ms = int(ms)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, millis = divmod(ms, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

def build_srt_from_chunks(results, timestamps):
    srt, idx = "", 1
    for text, (start, end) in zip(results, timestamps):
        if not text.strip():
            continue
        srt += f"{idx}\n{ms_to_srt_time(start)} --> {ms_to_srt_time(end)}\n{text.strip()}\n\n"
        idx += 1
    return srt

# ================= FILE READ (documents) =================
def read_file(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        return " ".join([p.extract_text() or "" for p in reader.pages])
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return " ".join([p.text for p in doc.paragraphs])
    else:
        return file.read().decode("utf-8", errors="ignore")

# ================= SUBTITLE (from plain text, no timing source) =================
def generate_srt(text):
    lines = [l for l in text.split(".") if l.strip()]
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
    "Video Reader",
    "Batch",
    "Podcast",
    "Subtitle",
    "Analytics",
    "History"
])

# ================= TAB 1: TTS =================
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

# ================= TAB 2: STT (advanced) =================
with tabs[1]:
    st.subheader("🗣️ Speech → Text")
    st.caption("Now supports WAV, MP3, M4A, OGG and FLAC, plus long-audio chunking and multi-language recognition.")

    file = st.file_uploader(
        "Upload audio",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
        key="stt_upload"
    )
    stt_lang_label = st.selectbox("Spoken language", list(STT_LANGUAGES.keys()), key="stt_lang")
    stt_translate_to = st.selectbox(
        "Translate transcript to (optional)",
        ["None"] + list(LANGUAGES.keys()),
        key="stt_translate"
    )

    if file:
        st.audio(file)

    if file and st.button("Transcribe", key="stt_button"):
        with st.spinner("Loading audio..."):
            file.seek(0)
            audio = load_audio_segment(file)
            duration_s = len(audio) / 1000

        st.caption(f"Duration: {duration_s:.1f}s — splitting into ~30s chunks for accurate recognition.")
        progress = st.progress(0)
        results, timestamps = transcribe_long_audio(
            audio,
            language=STT_LANGUAGES[stt_lang_label],
            chunk_ms=30000,
            progress_cb=lambda p: progress.progress(p)
        )
        transcript = " ".join([r for r in results if r and not r.startswith("[STT")]).strip()

        if not transcript:
            st.error("Could not recognize any speech. Try a clearer recording or different language.")
        else:
            if stt_translate_to != "None":
                transcript_display = GoogleTranslator(
                    source='auto', target=LANGUAGES[stt_translate_to]
                ).translate(transcript)
            else:
                transcript_display = transcript

            st.text_area("Transcript", transcript_display, height=200)
            word_count = len(transcript_display.split())
            st.caption(f"{word_count} words • {len(results)} chunk(s) processed")

            col1, col2 = st.columns(2)
            with col1:
                st.download_button("Download Transcript (.txt)", transcript_display, "transcript.txt")
            with col2:
                srt = build_srt_from_chunks(results, timestamps)
                st.download_button("Download Subtitles (.srt)", srt, "transcript.srt")

            add_history("STT")

# ================= TAB 3: VIDEO READER (new) =================
with tabs[2]:
    st.subheader("🎬 Video Reader")
    st.caption("Upload a video, extract the audio track, and transcribe it into text and timed subtitles.")

    video_file = st.file_uploader(
        "Upload video",
        type=["mp4", "mov", "mkv", "avi", "webm"],
        key="video_upload"
    )
    video_lang_label = st.selectbox("Spoken language", list(STT_LANGUAGES.keys()), key="video_lang")
    chunk_len = st.slider("Chunk length for transcription (seconds)", 10, 60, 30, key="video_chunk")

    if video_file:
        st.video(video_file)

    if video_file and st.button("Extract & Transcribe", key="video_button"):
        with st.spinner("Extracting audio track from video..."):
            video_file.seek(0)
            audio = load_audio_segment(video_file)
            duration_s = len(audio) / 1000

        st.caption(f"Video duration: {duration_s:.1f}s")
        progress = st.progress(0)
        results, timestamps = transcribe_long_audio(
            audio,
            language=STT_LANGUAGES[video_lang_label],
            chunk_ms=chunk_len * 1000,
            progress_cb=lambda p: progress.progress(p)
        )
        transcript = " ".join([r for r in results if r and not r.startswith("[STT")]).strip()

        if not transcript:
            st.error("No speech detected in this video's audio track.")
        else:
            st.text_area("Video Transcript", transcript, height=220)
            word_count = len(transcript.split())
            st.caption(f"{word_count} words • {duration_s:.1f}s of audio • {len(results)} chunk(s)")

            srt = build_srt_from_chunks(results, timestamps)

            audio_out = io.BytesIO()
            audio.export(audio_out, format="mp3")
            audio_out.seek(0)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("Download Transcript (.txt)", transcript, "video_transcript.txt")
            with col2:
                st.download_button("Download Subtitles (.srt)", srt, "video_subtitles.srt")
            with col3:
                st.download_button("Download Extracted Audio (.mp3)", audio_out, "extracted_audio.mp3")

            add_history("Video Reader")

# ================= TAB 4: BATCH =================
with tabs[3]:
    st.subheader("Batch Processing")

    files = st.file_uploader("Upload files", accept_multiple_files=True, key="batch_upload")

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

# ================= TAB 5: PODCAST =================
with tabs[4]:
    st.subheader("🎧 Podcast Mode")

    text = st.text_area("Podcast Script", key="podcast_text")
    music = st.file_uploader("Music", key="podcast_music")

    if text and music and st.button("Create"):
        audio = podcast_mode(text, music)
        st.audio(audio)

# ================= TAB 6: SUBTITLE (plain text) =================
with tabs[5]:
    st.subheader("Subtitle Generator (from text)")
    st.caption("For subtitles synced to real audio/video timing, use the STT or Video Reader tabs instead.")

    text = st.text_area("Paste text", key="subtitle_text")

    if st.button("Generate SRT"):
        srt = generate_srt(text)
        st.download_button("Download", srt, "subtitles.srt")

# ================= TAB 7: ANALYTICS =================
with tabs[6]:
    st.subheader("Analytics")

    data = {}
    for h in st.session_state.history:
        data[h["action"]] = data.get(h["action"], 0) + 1

    st.bar_chart(data)

# ================= TAB 8: HISTORY =================
with tabs[7]:
    st.subheader("History")

    for h in st.session_state.history[::-1]:
        st.write(h)
