import pyttsx3
import datetime            # ✅ Only module import — do NOT use `from datetime import datetime`
import wikipedia
import webbrowser
import pyautogui
import pywhatkit
import random
import os
import json
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import subprocess
import time
import threading
import tkinter as tk
from tkinter import messagebox



# === Global Variables ===
user_name = "Preksha"
language_preference = "english"
user_emotion = "neutral"
convo_memory = []

# === Initialize TTS Engine ===
engine = pyttsx3.init()
engine.setProperty("voice", engine.getProperty('voices')[0].id)
engine.setProperty('rate', 150)


# --- To-Do List Setup ---
tasks = []

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
    done = sum(1 for t in tasks if t["done"])
    left = total - done
    speak(f"End of day summary: {done} completed, {left} remaining out of {total} tasks.")

# === Memory Load/Save ===
def load_memory():
    global user_name, language_preference
    if os.path.exists("memory.json"):
        with open("memory.json", "r") as f:
            data = json.load(f)
            user_name = data.get("user_name", user_name)
            language_preference = data.get("language", language_preference)

def save_memory():
    with open("memory.json", "w") as f:
        json.dump({
            "user_name": user_name,
            "language": language_preference
        }, f)

# === Speak Function ===
def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

# === Audio Listener (No PyAudio) ===
def listen_for_command(duration=5):
    fs = 44100
    filename = "temp_input.wav"

    try:
        print("🎤 Listening via sounddevice...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()
        recording_int16 = np.int16(recording * 32767)
        write(filename, fs, recording_int16)

        recognizer = sr.Recognizer()
        with sr.AudioFile(filename) as source:
            audio_data = recognizer.record(source)

        query = recognizer.recognize_google(audio_data, language="en-IN")
        print(f"You: {query}")
        os.remove(filename) 
        return query.lower()

    except sr.UnknownValueError:
        print("🤖 Could not understand audio.")
        return ""
    except sr.RequestError:
        print("⚠️ Could not connect to recognition service.")
        return ""
    except Exception as e:
        print(f"Error: {e}")
        return ""

# === Greeting ===
def greet_user():
    hour = datetime.datetime.now().hour
    greet = "Good morning!" if 6 <= hour < 12 else "Good afternoon!" if hour < 18 else "Good evening!"
    speak(f"Welcome back, {user_name}!")
    speak(greet)
    tell_time()
    tell_date()
    speak("Say 'Jarvis' when you need me.")

# === Time & Date ===
def tell_time():
    speak("The time is " + datetime.datetime.now().strftime("%I:%M %p"))

def tell_date():
    speak("Today's date is " + datetime.datetime.now().strftime("%B %d, %Y"))

# === Screenshot ===
def take_screenshot():
    filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pyautogui.screenshot().save(filename)
    speak("Screenshot taken and saved.")

# === Emotion Detection ===
emotions = ["sad", "happy", "angry", "excited"]
def detect_emotion(query):
    for emotion in emotions:
        if emotion in query:
            return emotion
    return None

def contextual_reply():
    if user_emotion == "sad":
        return "I'm here for you. Want a joke or something positive?"
    elif user_emotion == "happy":
        return "I love your vibe! Want a fun fact?"
    elif user_emotion == "angry":
        return "Take a deep breath. I'm here if you need me."
    elif user_emotion == "excited":
        return "Wow! What's got you so excited?"
    return "Tell me more."

# === Keyword Responses ===
keywords = {
    "hello": ["Hello {user}, how can I help you today?"],
    "how are you": ["I'm doing well, {user}. Thanks for asking!"],
    "your name": ["I am Jarvis, your voice assistant."],
    "what can you do": ["I can take screenshots, tell time, search Wikipedia, play songs, and more!"],
    "motivate me": ["You're stronger than you think, {user}!", "Keep going, you're doing great!"],
    "joke": ["Why don’t scientists trust atoms? Because they make up everything!", "I'm on a seafood diet. I see food, and I eat it!"]
}

def close_browsers():
    # Closes common browser applications (Chrome, Edge, etc.)
    speak("Closing browser tabs like Google, YouTube, or Instagram.")
    os.system("taskkill /f /im chrome.exe >nul 2>&1")
    os.system("taskkill /f /im msedge.exe >nul 2>&1")
    os.system("taskkill /f /im firefox.exe >nul 2>&1")
    os.system("taskkill /f /im instagram.exe >nul 2>&1")


# === Handle Small Talk & Settings ===
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
    elif "speak english" in query:
        language_preference = "english"
        save_memory()
        speak("I will speak in English from now on.")
        return True

    emotion = detect_emotion(query)
    if emotion:
        user_emotion = emotion
        speak(f"I noticed you're feeling {user_emotion}. {contextual_reply()}")
        return True

    for key in keywords:
        if key in query:
            speak(random.choice(keywords[key]).format(user=user_name))
            return True

    return False

# === Main Command Handler ===
def handle_command(query):
    if any(x in query for x in ["bye", "shutdown", "shut down", "quit", "exit"]):
        speak(f"Goodbye {user_name}, shutting down now.")
        exit()

    if have_convo(query):
        return

    if "time" in query:
        tell_time()
    elif "date" in query:
        tell_date()
    elif "screenshot" in query:
        take_screenshot()
    elif "wikipedia" in query:
        try:
            speak("Searching Wikipedia...")
            result = wikipedia.summary(query.replace("wikipedia", ""), sentences=2)
            speak(result)
        except:
            speak("Sorry, nothing found.")
    elif "open youtube" in query:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube.")
    elif "open google" in query:
        webbrowser.open("https://www.google.com")
        speak("Opening Google.")
    elif "open instagram" in query:
        webbrowser.open("https://www.instagram.com")
        speak("Opening Instagram.")
    elif "open chatgpt" in query:
        webbrowser.open("https://www.chatgpt.com")
        speak("Opening Chatgpt.")
    elif "play" in query:
        song = query.replace("play", "").strip()
        speak(f"Playing {song} on YouTube.")
        pywhatkit.playonyt(song)
    elif "close google" in query or "close youtube" in query or "close instagram" in query:
        close_browsers()
    elif "add task" in query:
        task = query.replace("add task", "").strip()
        if task:
            add_task(task)
        else:
            speak("Please tell me the task to add.")
    elif "complete task" in query or "mark task" in query:
        task = query.replace("complete task", "").replace("mark task", "").strip()
        if task:
            complete_task(task)
        else:
            speak("Please tell me which task to complete.")
    elif "summary" in query or "tasks summary" in query:
        end_of_day_summary()
   
def daily_summary_scheduler():
    while True:
        now = datetime.datetime.now()
        # Check at 23:59 each day
        if now.hour == 23 and now.minute == 59:
            end_of_day_summary()
            time.sleep(60)
        time.sleep(30)

threading.Thread(target=daily_summary_scheduler, daemon=True).start()


import webbrowser
import urllib.parse

import urllib.parse
import webbrowser

def handle_query(query: str):
    trigger = "search for"
    low = query.lower()
    
    if trigger in low:
        # Find the index after the trigger phrase
        start_index = low.find(trigger) + len(trigger)
        search_term = query[start_index:].strip()
        
        if search_term:
            encoded = urllib.parse.quote_plus(search_term)
            url = f"https://www.google.com/search?q={encoded}"
            print(f"🔍 Searching for: '{search_term}'")
            webbrowser.open(url)
        else:
            print("⚠️ Please specify what you'd like to search for.")
    else:
        print("ℹ️ No search command detected.")

# === Main Loop ===
if __name__ == "__main__":
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
