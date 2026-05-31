import sys
import os
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MiloWindow
from src.ui.setup_wizard import SetupWizard # Import the wizard

def main():
    app = QApplication(sys.argv)
    
    # Check for API Key
    if not os.path.exists(".env"):
        wizard = SetupWizard()
        if wizard.exec() != QDialog.Accepted:
            return # Exit if they close the wizard without saving

    # Now launch the app
    window = MiloWindow()
    window.show()
    sys.exit(app.exec())
