from PySide6.QtWidgets import QApplication
from src.ui.main_window import MiloWindow
from src.core.voice_engine import VoiceEngine
from src.core.brain import Brain
import sys

def main():
    app = QApplication(sys.argv)
    window = MiloWindow()
    brain = Brain(window)
    voice = VoiceEngine(window, brain)
    
    window.show()
    voice.start() 
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
