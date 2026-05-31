MILO - Machine Intelligence Liaison Operator
MILO is a JARVIS-inspired AI desktop assistant designed for task automation, self-healing code generation, and interactive visualization. It utilizes the Google Gemini API for its intelligence and runs local processes for speech and system operations.  
MD
+ 1

Prerequisites
Before running MILO, ensure you have the following installed on your system:

Python 3.9 or higher

Git

Installation
Clone the repository to your local machine:

Bash
git clone https://github.com/greyisgreat/Milo-Ai-V3
cd Milo-Ai-V3

2. Install the required Python dependencies:
   ```bash
   pip install PySide6 psutil google-generativeai SpeechRecognition pyttsx3 python-dotenv
Note for Linux users: You may also need to install system audio dependencies:

Bash
sudo apt install python3-pyaudio portaudio19-dev
Configuration
In the root directory of the project, create a new file named .env.

Open the .env file and add your Google Gemini API key:

Plaintext
GEMINI_API_KEY=your_actual_api_key_here
3. Save the file. Ensure this file is never committed to GitHub.

## How to Run MILO

1. Open your terminal or command prompt.
2. Navigate to the project directory.
3. Run the application using the following command:
   ```bash
   python main.py
Architecture Overview
MILO is built with a modular architecture:  
MD
+ 1

Core: Handles the Gemini API brain, voice processing, and self-healing logic.  
MD
+ 1

Tools: Contains the system operation dispatcher for executing local computer tasks.  
MD
+ 1

UI: A PySide6-based glassmorphism interface for interaction and visualization[cite: 1, 6].
