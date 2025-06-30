#!/usr/bin/env python3
import sys, json
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)


import json
import datetime
import wikipedia
import webbrowser
import pyautogui
import pywhatkit
import random
import os
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import subprocess
import time
import threading
import tkinter as tk
from tkinter import messagebox
import pyttsx3

# === Global Variables ===
user_name = "Preksha"
language_preference = "english"
user_emotion = "neutral"
convo_memory = []
tasks = []

# === TTS Setup ===
engine = pyttsx3.init()
def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

# === Task functions ===
def add_task(task):
    tasks.append({"task": task, "done": False})
    speak(f"Added task: {task}")

def complete_task(task):
    for t in tasks:
        if not t["done"] and task in t["task"]:
            t["done"] = True
            speak(f"Marked '{t['task']}' as done.")
            return True
    speak(f"No matching pending task found for '{task}'")
    return False

def end_of_day_summary():
    total = len(tasks)
    done = sum(t["done"] for t in tasks)
    left = total - done
    speak(f"End of day summary: {done} completed, {left} remaining out of {total} tasks.")

# === Memory functions ===
def load_memory():
    global user_name, language_preference
    if os.path.exists("memory.json"):
        with open("memory.json", "r") as f:
            data = json.load(f)
            user_name = data.get("user_name", user_name)
            language_preference = data.get("language", language_preference)

def save_memory():
    with open("memory.json", "w") as f:
        json.dump({"user_name": user_name, "language": language_preference}, f)
def greet_user():
    hour = datetime.datetime.now().hour
    greet = "Good morning!" if 6 <= hour < 12 else "Good afternoon!" if hour < 18 else "Good evening!"
    speak(f"Welcome back, {user_name}!")
    speak(greet)
    tell_time()
    tell_date()
    speak("Say 'Jarvis' when you need me.")
# === Utility functions ===
def tell_time():
    speak("The time is " + datetime.datetime.now().strftime("%I:%M %p"))

def tell_date():
    speak("Today's date is " + datetime.datetime.now().strftime("%B %d, %Y"))

def take_screenshot():
    fname = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pyautogui.screenshot().save(fname)
    speak("Screenshot taken and saved.")

# === Emotion and keywords ===
emotions = ["sad", "happy", "angry", "excited"]
keywords = {
    "hello""hey": ["Hello {user}, how can I help you today?"],
    "how are you": ["I'm doing well, {user}. Thanks for asking!"],
    "your name": ["I am Jarvis, your voice assistant."],
    "what can you do": ["I can take screenshots, tell time, search Wikipedia, play songs, and more!"],
    "motivate me": ["You're stronger than you think, {user}!", "Keep going, you're doing great!"],
    "joke": ["Why don’t scientists trust atoms? Because they make up everything!", "I'm on a seafood diet. I see food, and I eat it!"],
    "hie":["Hello {user}, how can I help you today?"],
    "hii":["Hello {user}, how can I help you today?"],
    "i love you":["Thankyou! Love You more!"],
    "yes":["okay yaay!"],
    "no":["ohh okok"],
    "okay":["glad to help"],
    "hey": ["Hello {user}, how can I help you today?"],

}

def detect_emotion(query):
    for e in emotions:
        if e in query:
            return e
    return None

def contextual_reply():
    if user_emotion == "sad":
        return "I'm here for you. Want a joke or something positive?"
    if user_emotion == "happy":
        return "I love your vibe! Want a fun fact?"
    if user_emotion == "angry":
        return "Take a deep breath. I'm here if you need me."
    if user_emotion == "excited":
        return "Wow! What's got you so excited?"
    return "Tell me more."

def have_convo(query):
    global user_name, user_emotion, language_preference
    convo_memory.append(query)
    if "call me" in query:
        user_name = query.replace("call me", "").strip().capitalize()
        save_memory()
        speak(f"Okay, I’ll call you {user_name} now.")
        return True
    if "speak hindi" in query:
        language_preference = "hindi"
        save_memory()
        speak("अब से मैं हिंदी में बात करूँगा।")
        return True
    if "speak english" in query:
        language_preference = "english"
        save_memory()
        speak("I will speak in English from now on.")
        return True
    e = detect_emotion(query)
    if e:
        user_emotion = e
        speak(f"I noticed you're feeling {user_emotion}. {contextual_reply()}")
        return True
    for key, resps in keywords.items():
        if key in query:
            speak(random.choice(resps).format(user=user_name))
            return True
    return False

# === Command handler function ===
def handle_command(query):
   
    q = query.lower()
    if any(x in q for x in ["bye", "shutdown", "exit", "quit"]):
        speak(f"Goodbye {user_name}, shutting down now.")
        sys.exit()
    if have_convo(q):
        return
    if "time" in q: tell_time()
    elif "date" in q: tell_date()
    elif "screenshot" in q: take_screenshot()
    elif "wikipedia" in q:
        speak("Searching Wikipedia...")
        try:
            res = wikipedia.summary(q.replace("wikipedia", ""), sentences=2)
            speak(res)
        except:
            speak("Sorry, nothing found.")
    elif "open youtube" in q:
        webbrowser.open("https://www.youtube.com"); speak("Opening YouTube.")
    elif "open google" in q:
        webbrowser.open("https://www.google.com"); speak("Opening Google.")
    elif "open instagram" in q:
        webbrowser.open("https://www.instagram.com"); speak("Opening Instagram.")
    elif "open chatgpt" in q:
        webbrowser.open("https://www.chatgpt.com"); speak("Opening ChatGPT.")
    elif "play" in q:
        song = q.replace("play", "").strip()
        speak(f"Playing {song} on YouTube.")
        pywhatkit.playonyt(song)
    elif any(x in q for x in ["close google", "close youtube", "close instagram"]):
        for prog in ["chrome.exe", "msedge.exe", "firefox.exe", "instagram.exe"]:
            os.system(f"taskkill /f /im {prog} >nul 2>&1")
        speak("Closed browsers.")
    elif "add task" in q:
        add_task(q.replace("add task", "").strip())
    elif any(x in q for x in ["complete task", "mark task"]):
        complete_task(q.replace("complete task", "").replace("mark task", "").strip())
    elif "summary" in q:
        end_of_day_summary()
   

# === Audio capture ===
def listen_for_command(duration=5):
    fs = 44100; filename = "temp_input.wav"
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    write(filename, fs, recording)
    r = sr.Recognizer()
    with sr.AudioFile(filename) as src:
        audio = r.record(src)
    os.remove(filename)
    try:
        q = r.recognize_google(audio, language="en-IN")
        print(f"You: {q}")
        return q.lower()
    except:
        return ""

# === Scheduler thread ===
def daily_summary_scheduler():
    while True:
        now = datetime.datetime.now()
        if now.hour == 23 and now.minute == 59:
            end_of_day_summary()
            time.sleep(60)
        time.sleep(30)

threading.Thread(target=daily_summary_scheduler, daemon=True).start()

# === New helper to capture text replies ===
def handle_text_command(query: str) -> str:
    captured = ""
    def _capture(text):
        nonlocal captured
        if not captured:
            captured = text

    orig = globals()['speak']
    globals()['speak'] = _capture

    try:
        handle_command(query)
    except SystemExit:
        captured = f"Goodbye, {user_name}."
    finally:
        globals()['speak'] = orig

    if not captured:
        fallback = "hey srry i'm still learning.."
        speak(fallback)
        return fallback


    return captured  # ← IMPORTANT: return captured text

# ...

def main_loop():
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        data = json.loads(raw)
        reply = handle_text_command(data['message']) or ""
        resp = {"id": data['id'], "reply": reply}
        print(json.dumps(resp), flush=True)

if __name__ == "__main__":
    main_loop()
    load_memory()
    greet_user()

    while True:
        print("\n🔎 Waiting for wake word...")
        wake = listen_for_command(duration=4)

        if "jarvis" in wake:
            speak(f"Yes {user_name}, I’m listening.")

            silent_count = 0
            while True:
                user_input = listen_for_command(duration=5)
                if user_input.strip():
                    handle_command(user_input)
                    silent_count = 0
                else:
                    silent_count += 1
                    if silent_count == 1:
                        speak("I'm still here. Say more when you're ready.")
                    elif silent_count >= 2:
                        speak("No response. Going back to sleep.")
                        break
