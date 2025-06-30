# Jarvis – Your Personal Voice Assistant 🤖

A powerful, voice-activated AI assistant built in Python—powered by ChatGPT and extendable to handle your everyday tasks.

---

## 🚀 Features

- **Wake-word detection** ("Hey Jarvis") with speech-to-text (Whisper/Vosk).
- **Chat-based intelligence** via OpenAI GPT‑3.5/4 API.
- **Voice output** using pyttsx3, gTTS, or Coqui TTS.
- **Utility skills**: weather reports, system stats, Wikipedia lookup, email, screenshot, notes, jokes, and more.
- **Plugin-ready architecture**—add new commands via modular scripts.

---

## 🛠️ Requirements

- **Python 3.8+**
- Microphone & speaker
- API Keys:
  - `OPENAI_API_KEY` – required
  - Optional: `WEATHER_API_KEY`, `WOLFRAM_API_KEY`, `NEWS_API_KEY`
- Recommended packages: `SpeechRecognition`, `pyttsx3` or `gTTS`, `openai`, plus others.

---

## ⚡ Installation

git clone https://github.com/yourusername/jarvis.git
cd jarvis
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # insert your API keys
python main.py

