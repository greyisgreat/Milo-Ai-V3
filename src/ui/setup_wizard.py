from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
import os

class SetupWizard(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("M.I.L.O Initial Setup")
        layout = QVBoxLayout()
        
        self.label = QLabel("Enter your Gemini API Key to begin:")
        layout.addWidget(self.label)
        
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.Password) # Hides the key
        layout.addWidget(self.key_input)
        
        self.submit_btn = QPushButton("Save & Launch")
        self.submit_btn.clicked.connect(self.save_key)
        layout.addWidget(self.submit_btn)
        
        self.setLayout(layout)

    def save_key(self):
        key = self.key_input.text()
        with open(".env", "w") as f:
            f.write(f"GEMINI_API_KEY={key}")
        self.accept() # Closes the wizard
