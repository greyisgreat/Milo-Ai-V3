import speech_recognition as sr
import pyttsx3
import threading
from PySide6.QtCore import QThread, Signal

class VoiceEngine(QThread):
    def __init__(self, window, brain):
        super().__init__()
        self.window = window
        self.brain = brain
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def run(self):
        """Continuous listening loop."""
        with sr.Microphone() as source:
            while True:
                try:
                    audio = self.recognizer.listen(source)
                    text = self.recognizer.recognize_google(audio)
                    self.window.display_user(text)
                    self.brain.process(text)
                except Exception:
                    continue
