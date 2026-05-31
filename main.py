import os
import sys

def get_api_key():
    # Check if the key is already set
    if "GEMINI_API_KEY" not in os.environ:
        print("\n--- M.I.L.O SETUP ---")
        key = input("Please enter your Gemini API Key: ").strip()
        if key:
            os.environ["GEMINI_API_KEY"] = key
            return key
        else:
            print("API Key is required to run M.I.L.O.")
            sys.exit()
    return os.environ.get("GEMINI_API_KEY")

# Initialize the key
api_key = get_api_key()

# Your existing main logic goes here
print("M.I.L.O initialized successfully!")
# Example: start your AI loops below
