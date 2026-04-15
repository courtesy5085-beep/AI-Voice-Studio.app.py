import streamlit as st
from streamlit_lottie import st_lottie
import json
import requests
from gtts import gTTS
import speech_recognition as sr
from langdetect import detect
from deep_translator import GoogleTranslator
from pypdf import PdfReader
from docx import Document
from pydub import AudioSegment
import tempfile
import io
import time
from datetime import datetime
import edge_tts
import asyncio
import base64

# ---------- CONFIG ----------
st.set_page_config(
    page_title="AI Voice Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- LOAD LOTTIE ANIMATIONS ----------
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        return None

# Lottie URLs
LOTTIE_MIC = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_fjv8qxha.json")
LOTTIE_WAVE = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_UJNc2t.json")
LOTTIE_AI = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_x62chJ.json")
LOTTIE_SUCCESS = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_jz2rmsgk.json")

# ---------- ULTRA VFX CSS ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

    * { font-family: 'Space Grotesk', sans-serif; }

  .vfx-header {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 4rem 2rem;
        border-radius: 30px;
        text-align: center;
        color: white;
        box-shadow: 0 0 60px rgba(238, 119, 82, 0.6),
                    0 0 100px rgba(35, 166, 213, 0.4);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }

  .vfx-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 50px 50px;
        animation: moveGrid 20s linear infinite;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes moveGrid {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 50px); }
    }

  .vfx-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        text-shadow: 0 0 20px rgba(255,255,255,0.8),
                     0 0 40px rgba(238, 119, 82, 0.6);
        animation: glow 2s ease-in-out infinite alternate;
        position: relative;
        z-index: 1;
    }

    @keyframes glow {
        from { text-shadow: 0 0 20px rgba(255,255,255,0.8), 0 0 40px rgba(238, 119, 82, 0.6); }
        to { text-shadow: 0 0 30px rgba(255,255,255,1), 0 0 60px rgba(35, 166, 213, 0.8); }
    }

  .glass-card-vfx {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(25px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 24px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }

  .glass-card-vfx::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }

  .glass-card-vfx:hover::before {
        left: 100%;
    }

  .glass-card-vfx:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.5),
                    0 0 80px rgba(238, 119, 82, 0.3);
        border: 1px solid rgba(102, 126, 234, 0.6);
    }

  .neon-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 16px;
        padding: 1rem 3rem;
        font-weight: 700;
        font-size: 1.1rem;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.5),
                    0 0 40px rgba(102, 126, 234, 0.3);
        transition: all 0.3s;
    }

  .neon-button:hover {
        transform: scale(1.08) translateY(-3px);
        box-shadow: 0 0 30px rgba(102, 126, 234, 0.8),
                    0 0 60px rgba(118, 75, 162, 0.6),
                    0 0 90px rgba(102, 126, 234, 0.4);
    }

  .neon-button::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.5);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }

  .neon-button:active::after {
        width: 300px;
        height: 300px;
    }

  .metric-vfx {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4); }
        50% { box-shadow: 0 15px 50px rgba(102, 126, 234, 0.7); }
    }

  .metric-vfx h3 {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 0 10px rgba(255,255,255,0.5);
    }

  .typewriter {
        overflow: hidden;
        border-right:.15em solid #667eea;
        white-space: nowrap;
        margin: 0 auto;
        animation: typing 3.5s steps(40, end), blink-caret.75s step-end infinite;
    }

    @keyframes typing {
        from { width: 0 }
        to { width: 100% }
    }

    @keyframes blink-caret {
        from, to { border-color: transparent }
        50% { border-color: #667eea; }
    }

  .waveform {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 3px;
        height: 60px;
    }

  .wave-bar {
        width: 4px;
        background: linear-gradient(180deg, #667eea, #764ba2);
        border-radius: 10px;
        animation: wave 1.2s ease-in-out infinite;
    }

  .wave-bar:nth-child(1) { animation-delay: 0s; height: 20px; }
  .wave-bar:nth-child(2) { animation-delay: 0.1s; height: 40px; }
  .wave-bar:nth-child(3) { animation-delay: 0.2s; height: 60px; }
  .wave-bar:nth-child(4) { animation-delay: 0.3s; height: 40px; }
  .wave-bar:nth-child(5) { animation-delay: 0.4s; height: 20px; }
  .wave-bar:nth-child(6) { animation-delay: 0.5s; height: 50px; }
  .wave-bar:nth-child(7) { animation-delay: 0.6s; height: 30px; }

    @keyframes wave {
        0%, 100% { transform: scaleY(0.5); opacity: 0.5; }
        50% { transform: scaleY(1); opacity: 1; }
    }

  .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
 .stDeployButton {display: none;}
</style>

<!-- Particles Background -->
<canvas class="particles" id="particles"></canvas>
<script>
    const canvas = document.getElementById('particles');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const particles = [];
        for(let i = 0; i < 50; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2 + 1
            });
        }

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = 'rgba(102, 126, 234, 0.5)';

            particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;

                if(p.x < 0 || p.x > canvas.width) p.vx *= -1;
                if(p.y < 0 || p.y > canvas.height) p.vy *= -1;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();
            });

            requestAnimationFrame(animate);
        }
        animate();
    }
</script>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if 'history' not in st.session_state:
    st.session_state.history = []
if 'confetti' not in st.session_state:
    st.session_state.confetti = False

# ---------- HEADER WITH VFX ----------
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    if LOTTIE_MIC:
        st_lottie(LOTTIE_MIC, height=150, key="header_anim")

st.markdown("""
<div class="vfx-header">
    <h1 class="vfx-title">🎙️ AI VOICE STUDIO</h1>
    <p class="typewriter" style='font-size: 1.4rem; margin-top: 1rem; font-weight: 300;'>
        Next-Gen Text ↔ Speech | AI Translation | Edge TTS | Batch Processing
    </p>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR VFX ----------
with st.sidebar:
    if LOTTIE_AI:
        st_lottie(LOTTIE_AI, height=120, key="sidebar_ai")

    st.title("⚙️ VFX Control Panel")

    st.divider()
    engine = st.selectbox(
        "🎛️ TTS Engine",
        ["Edge TTS - Neural 🌟", "gTTS - Fast ⚡", "gTTS - Slow 🐌"]
    )

    st.divider()
    st.subheader("🎵 Voice FX")
    speed = st.slider("Speed", 0.5, 2.0, 1.0, 0.1)
    gender = st.radio("Voice", ["Female 👩", "Male 👨"], horizontal=True)

    st.divider()
    st.subheader("📊 Live Stats")
    col1, col2 = st.columns(2)
    col1.metric("Total", len(st.session_state.history), "🔥")
    col2.metric("Today", len([h for h in st.session_state.history if h.get('date') == datetime.now().date()]))

    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# ---------- FUNCTIONS ----------
LANGUAGES = {
    "🔍 Auto": "auto", "🇺🇸 English": "en", "🇵🇰 Urdu": "ur",
    "🇮🇳 Hindi": "hi", "🇸🇦 Arabic": "ar", "🇫🇷 French": "fr",
    "🇩🇪 German": "de", "🇪🇸 Spanish": "es", "🇨🇳 Chinese": "zh-cn",
    "🇯🇵 Japanese": "ja", "🇷🇺 Russian": "ru", "🇹🇷 Turkish": "tr"
}

EDGE_VOICES = {
    "en": {"Female 👩": "en-US-AriaNeural", "Male 👨": "en-US-GuyNeural"},
    "ur": {"Female 👩": "ur-PK-AsmaNeural", "Male 👨": "ur-PK-UzmaNeural"},
    "hi": {"Female 👩": "hi-IN-SwaraNeural", "Male 👨": "hi-IN-MadhurNeural"},
}

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

async def edge_tts_gen(text, lang, gender, speed):
    voice = EDGE_VOICES.get(lang, EDGE_VOICES["en"])[gender]
    rate = f"+{int((speed-1)*100)}%" if speed >= 1 else f"{int((speed-1)*100)}%"
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    fp = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            fp.write(chunk["data"])
    fp.seek(0)
    return fp

def text_to_speech(text, lang, engine, gender, speed):
    try:
        if "Edge" in engine:
            return asyncio.run(edge_tts_gen(text, lang, gender, speed))
        else:
            tts = gTTS(text=text, lang=lang, slow="Slow" in engine)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def read_pdf(file):
    text = ""
    try:
        reader = PdfReader(file)
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                text += f"\n=== Page {i+1} ===\n{page_text}\n"
    except:
        pass
    return text

def add_history(action, content, lang):
    st.session_state.history.insert(0, {
        "time": datetime.now().strftime("%I:%M %p"),
        "action": action,
        "content": content[:50],
        "lang": lang,
        "date": datetime.now().date()
    })
    if len(st.session_state.history) > 20:
        st.session_state.history.pop()

# ---------- CONFETTI FUNCTION ----------
def show_confetti():
    st.balloons()
    if LOTTIE_SUCCESS:
        st_lottie(LOTTIE_SUCCESS, height=200, key=f"success_{time.time()}")

# ---------- MAIN TABS ----------
tab1, tab2, tab3, tab4 = st.tabs([
    "🔊 Text → Speech VFX",
    "🎤 Speech → Text",
    "📄 Batch Converter",
    "📜 History"
])

# ---------- TAB 1: TTS VFX ----------
with tab1:
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="glass-card-vfx">', unsafe_allow_html=True)
        st.subheader("✍️ Enter Text with VFX")

        if LOTTIE_WAVE:
            st_lottie(LOTTIE_WAVE, height=80, key="wave_anim")

        text_input = st.text_area(
            "Text",
            height=200,
            placeholder="Type anything... Watch the magic happen! ✨",
            label_visibility="collapsed"
        )

        if text_input:
            words = len(text_input.split())
            chars = len(text_input)
            duration = round(words / 150, 1)

            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="metric-vfx"><h3>{words}</h3><p>Words</p></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="metric-vfx"><h3>{chars}</h3><p>Chars</p></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="metric-vfx"><h3>{duration}m</h3><p>Duration</p></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card-vfx">', unsafe_allow_html=True)
        st.subheader("🌍 Settings")

        lang_display = st.selectbox("Language", list(LANGUAGES.keys()))
        lang_code = LANGUAGES[lang_display]

        if lang_display == "🔍 Auto" and text_input:
            detected = detect_language(text_input)
            st.success(f"🎯 Detected: **{detected.upper()}**")
            lang_code = detected

        translate_on = st.toggle("🔄 Auto Translate?")
        if translate_on:
            target = st.selectbox("To", list(LANGUAGES.keys())[1:], index=0)

        st.markdown('</div>', unsafe_allow_html=True)

    # Waveform Visualization
    st.markdown("""
    <div class="glass-card-vfx">
        <h4 style='text-align: center; margin-bottom: 1rem;'>🎵 Audio Waveform Preview</h4>
        <div class="waveform">
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🎵 GENERATE WITH VFX", type="primary", use_container_width=True):
        if not text_input.strip():
            st.warning("⚠️ Please enter text")
        else:
            progress = st.progress(0)
            status = st.empty()

            status.text("🔄 Processing...")
            progress.progress(25)
            time.sleep(0.3)

            final_text = text_input
            final_lang = lang_code

            if translate_on:
                status.text("🌍 Translating...")
                progress.progress(50)
                try:
                    final_text = GoogleTranslator(
                        source='auto',
                        target=LANGUAGES[target]
                    ).translate(text_input)
                    final_lang = LANGUAGES[target]
                    with st.expander("📝 Translation"):
                        st.info(final_text)
                except:
                    st.warning("Translation failed")

            status.text("🎙️ Generating audio...")
            progress.progress(75)

            audio = text_to_speech(final_text, final_lang, engine, gender, speed)

            progress.progress(100)
            status.text("✅ Complete!")

            if audio:
                show_confetti()
                st.success(f"✅ Generated! Lang: {final_lang.upper()}")

                st.audio(audio, format="audio/mp3")

                audio.seek(0)
                st.download_button(
                    "⬇️ Download MP3",
                    data=audio,
                    file_name=f"vfx_voice_{int(time.time())}.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )

                add_history("TTS-VFX", text_input, final_lang)
                time.sleep(1)
                progress.empty()
                status.empty()

# ---------- TAB 2: STT ----------
with tab2:
    st.markdown('<div class="glass-card-vfx">', unsafe_allow_html=True)
    st.subheader("🎤 Speech Recognition VFX")

    uploaded_audio = st.file_uploader("Upload Audio", type=["wav", "mp3", "ogg", "m4a"])

    if uploaded_audio:
        st.audio(uploaded_audio)
        lang_stt = st.selectbox("Audio Language", ["en-US", "ur-PK", "hi-IN", "ar-SA"])

        if st.button("📝 Transcribe", type="primary", use_container_width=True):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(uploaded_audio.read())
                temp_path = tmp.name

            if not uploaded_audio.name.endswith(".wav"):
                sound = AudioSegment.from_file(temp_path)
                temp_wav = temp_path + "_conv.wav"
                sound.export(temp_wav, format="wav")
                temp_path = temp_wav

            with st.spinner("🧠 AI Listening..."):
                recognizer = sr.Recognizer()
                with sr.AudioFile(temp_path) as source:
                    recognizer.adjust_for_ambient_noise(source)
                    audio_data = recognizer.record(source)
                try:
                    result = recognizer.recognize_google(audio_data, language=lang_stt)
                    st.success("✅ Done!")
                    st.text_area("Result", result, height=200)
                    add_history("STT", result, lang_stt)
                    show_confetti()
                except:
                    st.error("❌ Could not understand audio")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- TAB 3: BATCH ----------
with tab3:
    st.markdown('<div class="glass-card-vfx">', unsafe_allow_html=True)
    st.subheader("📁 Batch Converter VFX")

    files = st.file_uploader("Drop Multiple Files", type=["pdf", "docx", "txt"], accept_multiple_files=True)

    if files:
        st.success(f"✅ {len(files)} files loaded")

        for idx, file in enumerate(files):
            with st.expander(f"📄 {file.name}", expanded=(idx==0)):
                content = read_pdf(file) if file.name.endswith('.pdf') else file.read().decode('utf-8', errors='ignore')

                if content.strip():
                    st.text_area("Preview", content[:1000], height=100, key=f"prev_{idx}")

                    if st.button("🔊 Convert", key=f"conv_{idx}"):
                        lang = detect_language(content)
                        audio = text_to_speech(content[:3000], lang, engine, gender, speed)
                        if audio:
                            st.audio(audio)
                            st.download_button("⬇️ Download", audio, f"{file.name}.mp3", key=f"dl_{idx}")
                  
