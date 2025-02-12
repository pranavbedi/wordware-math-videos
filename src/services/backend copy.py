from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import requests
import subprocess
import re
import os
import io

app = FastAPI()

# Add CORS middleware to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TopicRequest(BaseModel):
    topic: str

@app.post("/generate-video")
async def generate_video(request: TopicRequest):
    topic = request.topic

    # === Configuration for Wordware API ===
    API_KEY = "ww-58cO6lATztJ6wlGeF8AUysdFpnOYQBykTaL3ZkJt7n4Wr5b51BKFvw"            # Replace with your actual API key
    APP_ID = "965156f5-acb1-4199-b36b-3500af6f04bb"
    url = f"https://app.wordware.ai/api/released-app/{APP_ID}/run"
    payload = {
        "inputs": {
            "Topic": topic
        },
        "version": "^1.0"
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}

    # === 1. Call the Wordware API and capture the streaming response entirely ===
    response = requests.post(url, json=payload, headers=headers, stream=True)
    if response.status_code != 200:
        try:
            error_details = response.json()
        except Exception:
            error_details = response.text
        raise HTTPException(status_code=response.status_code,
                            detail=f"Wordware API request failed: {error_details}")

    # We'll collect all lines into an in-memory buffer
    all_data = io.StringIO()

    for chunk in response.iter_lines():
        if chunk:  # ignore keep-alive chunks
            decoded = chunk.decode("utf-8", errors="replace")
            all_data.write(decoded + "\n")

    # === 2. Write the entire streaming response to `response.txt` ===
    response_txt_path = "response.txt"
    with open(response_txt_path, "w", encoding="utf-8") as f:
        f.write(all_data.getvalue())

    # === 3. Run `extract_animation_python.py response.txt` to extract the Manim code ===
    try:
        extract_result = subprocess.run(
            ["python", "extract_animation_python.py", response_txt_path],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction script failed:\n{e.stderr or e.stdout}"
        )

    # The script should print the extracted Python code to stdout
    extracted_python_code = extract_result.stdout.strip()
    if not extracted_python_code:
        raise HTTPException(
            status_code=500,
            detail="No Python code was extracted by extract_animation_python.py."
        )

    # === 4. Save the extracted code as `generated_manim.py` ===
    py_filename = "generated_manim.py"
    with open(py_filename, "w", encoding="utf-8") as f:
        f.write(extracted_python_code)

    # === 5. Run Manim on that newly generated script ===
    try:
        render_result = subprocess.run(
            ["manim", "-pql", py_filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Manim rendering failed:\n{e.output}"
        )

    output_text = render_result.stdout

    # Attempt to find the produced .mp4 path in Manim's output
    match = re.search(r"(?:Saved to|File [Ww]ritten to|Output saved to)[^\n]*:?\s*([^\s]+\.mp4)", output_text)
    if match:
        video_path = match.group(1)
    else:
        # If not found, guess the default location
        video_path = '.\services\media\videos\generated_manim\VolumeVisualization.mp4'

    return {
        "video_path": video_path,
        "response_file": os.path.abspath(response_txt_path),
        "python_code_file": os.path.abspath(py_filename),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
