# 🎙️ AI Voice Studio

**AI Voice Studio** is an all-in-one Streamlit application for AI-powered voice and document workflows — text-to-speech generation, voice transcription, translation, document and video reading, text-to-PDF export, and a usage dashboard, all in a single clean interface.

> This repository ships with placeholder AI logic so it runs immediately with no API keys. Swap in your preferred providers (OpenAI, Whisper, ElevenLabs, gTTS, etc.) to go live.

---

## ✨ Features

| Page | Description |
|---|---|
| 🎙️ **Playground** | Enter text, pick a voice, and generate speech with instant playback and download. |
| 🎧 **Voice to Text** | Record audio live (via microphone) or upload a file, then transcribe it to text. |
| 🌍 **Translator** | Translate text between languages and play back the translated result as audio. |
| 📄 **File Reader** | Upload a PDF, DOCX, or TXT file, extract its text, and have it read aloud. |
| 🎬 **Video Reader** | Upload an MP4, extract the audio track, and transcribe it to text. |
| 📝 **Text to PDF** | Paste in text and export a formatted, downloadable PDF. |
| 📊 **Dashboard** | View usage metrics and interactive charts (feature usage, language breakdown). |

---

## 🛠️ Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-voice-studio
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Push this project (with `app.py`, `requirements.txt`, and `README.md`) to a public or private GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"**, select your repository, branch, and set the main file path to `app.py`.
4. Under **Advanced settings → Secrets**, add any required environment variables (see below).
5. Click **Deploy**. Streamlit Cloud will install dependencies from `requirements.txt` and launch the app automatically.
6. Any time you push new commits to the connected branch, the app will redeploy automatically.

---

## 🔑 Environment Variables

To connect real AI providers (replacing the placeholder functions in `app.py`), configure the following:

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | Used for Whisper-based transcription and/or OpenAI text-to-speech and translation. |
| `ELEVENLABS_API_KEY` | Used for high-quality text-to-speech voice generation. |

**Local setup:** create a `.env` file (not committed to source control) or export variables in your shell:
```bash
export OPENAI_API_KEY="your-key-here"
export ELEVENLABS_API_KEY="your-key-here"
```

**Streamlit Cloud setup:** add these under your app's **Settings → Secrets** as:
```toml
OPENAI_API_KEY = "your-key-here"
ELEVENLABS_API_KEY = "your-key-here"
```

---

## 📦 Tech Stack

- [Streamlit](https://streamlit.io/) — UI framework
- [streamlit-mic-recorder](https://pypi.org/project/streamlit-mic-recorder/) — in-browser microphone recording
- [PyPDF2](https://pypi.org/project/PyPDF2/) / [python-docx](https://pypi.org/project/python-docx/) — document text extraction
- [moviepy](https://pypi.org/project/moviepy/) — video audio extraction
- [fpdf2](https://pypi.org/project/fpdf2/) — PDF generation
- [Plotly](https://plotly.com/python/) & [pandas](https://pandas.pydata.org/) — dashboard charts and data handling

---

## 📝 Notes

- All AI functionality (speech generation, transcription, translation) is currently stubbed with placeholder logic clearly marked with `# TODO` comments in `app.py`. The app is fully runnable out of the box for demo and UI-testing purposes.
- To go to production, replace each placeholder function (`generate_speech`, `transcribe_audio`, `translate_text`) with real API calls using the environment variables above.
