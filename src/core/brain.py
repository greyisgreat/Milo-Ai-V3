import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from src.tools.system_ops import execute

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class Brain:
    def __init__(self, window):
        self.window = window
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
    def process(self, transcript: str):
        """Sends transcript to Gemini to determine the action to take."""
        prompt = f"Given this user command: '{transcript}', return a JSON object with 'action' (the tool name) and 'args' (a dict of kwargs). Available actions: {['open_app', 'list_dir', 'system_status', 'shell_run', 'write_file']}."
        
        response = self.model.generate_content(prompt)
        try:
            intent = json.loads(response.text)
            self.window.display_system_event(f"Executing: {intent['action']}")
            
            # Execute the tool
            result = execute(intent['action'], **intent.get('args', {}))
            
            if result.success:
                self.window.display_milo_response(f"Done. Result: {result.data}")
            else:
                self.window.display_error(f"Action failed: {result.error}")
        except Exception as e:
            self.window.display_error(f"Brain processing error: {e}")
