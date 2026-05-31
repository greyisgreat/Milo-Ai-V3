import os
import sys
from PySide6.QtWidgets import QApplication, QInputDialog

def check_for_api_key():
    # If the environment doesn't have the key yet
    if "GEMINI_API_KEY" not in os.environ:
        # We need a temporary app instance to show the dialog if it's not already running
        app = QApplication.instance() or QApplication(sys.argv)
        
        # This creates the popup window
        key, ok = QInputDialog.getText(None, "M.I.L.O Setup", "Please enter your Gemini API Key:")
        
        if ok and key:
            # Set the key for this session
            os.environ["GEMINI_API_KEY"] = key
            return key
        else:
            sys.exit("API Key is required to run M.I.L.O.")
    return os.environ.get("GEMINI_API_KEY")

# CALL THIS IMMEDIATELY BEFORE YOUR APP STARTS
check_for_api_key()
