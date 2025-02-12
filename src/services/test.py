import os
import json
import requests
import logging
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve API key from environment variables
API_KEY = os.getenv("API_KEY")
APP_ID = "f1d78ef9-bbd0-4714-9ff4-a8a1caba7236"  # Replace with your actual APP_ID

if not API_KEY:
    raise RuntimeError("API_KEY is missing. Ensure the .env file is set up correctly.")

# Sample broken Python code to test the Wordware repair API
original_code = """
from manim import *

class TestScene(Scene):
    def construct(self):
        rect = Rectangle()
        self.play(FadeIn(rect))
        self.wait()
"""

# Simulated error message that would be returned by Manim
error_message = """
File 'test_manim.py', line 6
    self.play(FadeIn(rect))
    ^
IndentationError: expected an indented block
"""

def call_wordware_repair(original_code: str, error_message: str) -> str:
    """
    Calls the Wordware API and saves the entire raw response to a .txt file.
    """
    prompt = (
        f"{error_message}\n\n"
        "Original code:\n\n"
        f"{original_code}\n\n"
        "Please generate a corrected version of the animation Python code that compiles and runs with Manim Community Edition. "
        "Do not use Tex or Latex, and avoid using problematic identifiers like Front, Back, Out, etc."
    )

    url = f"https://app.wordware.ai/api/released-app/{APP_ID}/run"
    payload = {
        "inputs": {"Code": prompt},
        "version": "^1.0"
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}

    logging.info("Attempting to repair Manim code via Wordware API.")

    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()  # Raises an HTTPError for 4xx and 5xx responses

        # Open file to save raw API response
        output_file = "wordware_api_response.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    f.write(decoded_line + "\n")  # Save each response line to the file

        print(f"\n✅ Full API response saved to {output_file}")
        return output_file  # Return the file path

    except requests.RequestException as e:
        logging.error(f"Wordware API request failed: {e}")
        return None

# Run the test function
response_file = call_wordware_repair(original_code, error_message)

if response_file:
    print(f"\n✅ API response saved in: {response_file}")
else:
    print("\n❌ Failed to get response from Wordware API.")
