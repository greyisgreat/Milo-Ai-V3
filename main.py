import os
import sys
from PySide6.QtWidgets import QApplication

def get_api_key():
    # This prompts you for the key in the terminal
    print("--- M.I.L.O SETUP ---")
    key = input("Please paste your Gemini API Key here and press Enter: ").strip()
    if not key:
        print("Error: API Key is required.")
        sys.exit()
    os.environ["GEMINI_API_KEY"] = key
    return key

def main():
    # 1. Get the key
    api_key = get_api_key()
    
    # 2. Initialize the App
    app = QApplication(sys.argv)
    
    # 3. M.I.L.O Logic
    print("M.I.L.O is online.")
    
    # This is the line that actually runs the UI
    # sys.exit(app.exec())

if __name__ == "__main__":
    main()
