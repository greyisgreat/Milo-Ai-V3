import os
import sys
import psutil
from PySide6.QtWidgets import QApplication
# Add other imports here, e.g., your UI classes

def get_api_key():
    # If the environment already has the key (e.g., from Codespaces Secrets), use it
    if "GEMINI_API_KEY" in os.environ:
        return os.environ["GEMINI_API_KEY"]
    
    # Otherwise, prompt the user for the key
    print("\n--- M.I.L.O SETUP ---")
    key = input("Please paste your Gemini API Key here and press Enter: ").strip()
    
    if not key:
        print("Error: API Key is required to run M.I.L.O.")
        sys.exit()
        
    os.environ["GEMINI_API_KEY"] = key
    print("Key accepted.")
    return key

def main():
    # 1. Initialize API Key
    api_key = get_api_key()
    
    # 2. Start Application
    print("Starting M.I.L.O...")
    app = QApplication(sys.argv)
    
    # Here you would typically initialize your main UI window
    # window = MainWindow() 
    # window.show()
    
    # 3. Placeholder to keep the app running in Codespaces
    print("M.I.L.O is running (GUI not available in Codespaces).")
    
    # This prevents the script from exiting immediately
    # sys.exit(app.exec())

if __name__ == "__main__":
    main()
