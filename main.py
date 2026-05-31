import os
import sys

def get_api_key_from_user():
    print("--- M.I.L.O SETUP ---")
    # This command pauses the app and waits for you to type the key in the terminal
    key = input("Please paste your Gemini API Key here and press Enter: ").strip()
    return key

# Get the key directly from you
api_key = get_api_key_from_user()

if not api_key:
    print("No key provided. Exiting.")
    sys.exit()

# Now the app proceeds using the key you just typed
os.environ["GEMINI_API_KEY"] = api_key
print("Key accepted. M.I.L.O is starting...")

# [Rest of your existing code goes below this line]
