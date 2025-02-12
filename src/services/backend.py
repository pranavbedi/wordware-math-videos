from fastapi import FastAPI, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import json
import requests
import logging
import subprocess
import re
import os
import shutil
import io
import ffmpeg  # used to probe durations
import sys
sys.stdout.reconfigure(encoding="utf-8")

app = FastAPI()

load_dotenv()

API_KEY = os.getenv("API_KEY")

if not API_KEY :
    raise RuntimeError("API_KEY or APP_ID is missing. Ensure the .env file is set up correctly.")


logging.basicConfig(
    level=logging.INFO,  # Ensures INFO level messages are printed
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Ensures logs are printed to console
    ]
)
# Add CORS middleware to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to your domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TopicRequest(BaseModel):
    topic: str

# --- Helper functions ---

def find_audio_file(obj):
    """
    Recursively search through a nested dictionary/list structure
    to find a value corresponding to one of the keys:
    'Audio File', 'Audio', or 'audio_url'.
    Returns the first match found. If none is found, returns None.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ["Audio File", "Audio", "audio_url"] and isinstance(v, str):
                return v  # Return the first audio file URL found
            result = find_audio_file(v)  # Recursive search
            

            if result:
                logging.info("Audio File Found")
                return result
            
    elif isinstance(obj, list):
        for item in obj:
            result = find_audio_file(item)
            
            if result:
                logging.info("Audio File Found")
                return result
    return None

def extract_audio_file(file_path: str) -> str:
    """
    Reads the file (response.txt) and searches for 'Audio File',
    'Audio', or 'audio_url' in any JSON object. If found, it downloads
    the audio and returns the local filename. If none is found, returns None.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Extract top-level JSON chunks
    raw_objects = re.findall(r'(?s)\{.*?\}(?=\n\{|$)', content)

    for obj_text in raw_objects:
        try:
            parsed = json.loads(obj_text)
        except json.JSONDecodeError:
            continue  # Skip invalid JSON chunks

        audio_url = find_audio_file(parsed)
        if audio_url:
            # Download and save the audio file
            logging.info("Found Audio URL -> Attempting to download audio file")
            filename = _download_audio_file(audio_url)
            return filename  # Return the saved filename

    # If no valid audio file URL is found
    return None

def _download_audio_file(audio_url: str) -> str:
    """
    Helper function to download an audio file from a URL and return
    the local filename of the saved file.
    """
    response = requests.get(audio_url, stream=True)
    response.raise_for_status()  # Raise an error if download failed


    basename = "downloaded_audio.mp3"

    with open(basename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    logging.info("Audio File Downloaded")
    return basename

def get_duration(file_path: str) -> float:
    """
    Uses ffmpeg.probe to get the duration (in seconds) of the given media file.
    """
    try:
        probe = ffmpeg.probe(file_path)
        logging.info(f"{file_path}: Duration Found")
        return float(probe['format']['duration'])
    except Exception as e:
        raise Exception(f"Failed to get duration for {file_path}: {e}")

# --- New helper: call Wordware to repair the generated animation code ---
def call_wordware_repair(original_code: str, error_message: str) -> str:
    """
    Calls the Wordware API to repair the given Manim Python script based on the error message.
    Extracts and returns the repaired code from the streamed response.
    """
    prompt = (
        f"{error_message}\n\n"
        "Original code:\n\n"
        f"{original_code}\n\n"
        "Please generate a corrected version of the animation Python code that compiles and runs with Manim Community Edition. "
        "Do not use Tex or Latex, and avoid using problematic identifiers like Front, Back, Out, etc."
    )

    APP_ID = "f1d78ef9-bbd0-4714-9ff4-a8a1caba7236"    
    url = f"https://app.wordware.ai/api/released-app/{APP_ID}/run"
    payload = {
        "inputs": {"Code": prompt},
        "version": "^1.0"
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}

    logging.info("Attempting to repair Manim code via Wordware API.")

    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()  # Raises HTTPError for 4xx and 5xx responses

        repaired_code = ""

        for line in response.iter_lines():
            if line:
                try:
                    content = json.loads(line.decode("utf-8"))
                    value = content.get("value", {})

                    # Case 1: Collect code in "chunk"
                    if value.get("type") == "chunk" and isinstance(value.get("value"), str):
                        repaired_code += value["value"]

                    # Case 2: Final cleaned code in "outputs"
                    elif value.get("type") == "outputs":
                        outputs = value.get("values", {})
                        if "Cleaned Code" in outputs:
                            return outputs["Cleaned Code"]  # Return cleaned code immediately

                except json.JSONDecodeError:
                    logging.warning("Failed to decode response line: %s", line.decode("utf-8"))

        return repaired_code if repaired_code else None

    except requests.RequestException as e:
        logging.error(f"Wordware API request failed: {e}")
        return None


# --- New helper: run Manim rendering with repair attempts ---
def run_manim_render_with_repair(py_filename: str) -> subprocess.CompletedProcess:
    max_attempts = 5
    attempt = 0
    while attempt < max_attempts:
        try:
            logging.info("Attempt %s to generate video", attempt + 1)
            render_result = subprocess.run(
                ["manim", "-ql", py_filename, "--output_file", "default_video.mp4", "--fps", "90"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True
            )
            return render_result  # Rendering succeeded.
        except subprocess.CalledProcessError as e:
            error_message = e.output
            logging.error("Manim rendering attempt %s failed with error:\n%s", attempt + 1, error_message)
            # Read the current code from the file.
            with open(py_filename, "r", encoding="utf-8") as f:
                original_code = f.read()
            # Call Wordware to repair the code using the error output.
            repaired_code = call_wordware_repair(original_code, error_message)
            if repaired_code:
                # Write the repaired code back to the file.
                with open(py_filename, "w", encoding="utf-8") as f:
                    f.write(repaired_code)
                logging.info("Repaired code obtained from Wordware; retrying rendering...")
            else:
                logging.error("Wordware did not return any repaired code. Retrying with the existing code.")
            attempt += 1
          
    raise Exception(f"Manim rendering failed after {max_attempts} attempts.")


# --- Main processing function ---
def process_response_file(response_txt_path: str):
    """
    Runs the entire video-generation process using an existing response.txt.
    Returns a dictionary with file paths and details.
    """
    # (a) Extract the Animation Python code using your helper script.
    try:
        logging.info("Attempting to extract python code")
        extract_anim = subprocess.run(
            ["python", "extract_animation_python.py", response_txt_path],
            capture_output=True,
            text=True,
            check=True
        )
        extracted_animation_code = extract_anim.stdout.strip()
        if not extracted_animation_code:
            raise Exception("No Animation Python code was extracted.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Extraction of Animation Python failed:\n{e.stderr or e.stdout}")

    # (b) Extract the script text using your helper script.
    try:
        logging.info("Attempting to extract script")
        extract_script = subprocess.run(
            ["python", "find_script.py", response_txt_path],
            capture_output=True,
            text=True,
            check=True
        )
        extracted_script_text = extract_script.stdout.strip()
        if not extracted_script_text:
            raise Exception("No Script was extracted.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Script extraction failed:\n{e.stderr or e.stdout}")

    # (c) Extract the audio file info from the response.
    audio_file_info = extract_audio_file(response_txt_path)
    if not audio_file_info:
        raise Exception("No audio file info was found in the API response.")
    if audio_file_info.startswith("http"):
        try:
            audio_response = requests.get(audio_file_info)
            audio_response.raise_for_status()
            audio_file_local = "downloaded_audio.mp3"
            with open(audio_file_local, "wb") as f:
                f.write(audio_response.content)
        except Exception as e:
            raise Exception(f"Failed to download audio file: {str(e)}")
    else:
        audio_file_local = audio_file_info

    # === 2. Generate the Python file for Manim and run the animation script ===
    py_filename = "generated_manim.py"
    with open(py_filename, "w", encoding="utf-8") as f:
        f.write(extracted_animation_code)

    try:
        render_result = run_manim_render_with_repair(py_filename)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Manim rendering failed after repair: {e.output}")
    except Exception as e:
        raise Exception(f"Manim rendering failed after repair attempts: {str(e)}")

    output_text = render_result.stdout


    original_path = "./media/videos/generated_manim/480p90/default_video.mp4"
    video_path = "default_video.mp4"
    shutil.copy(original_path, video_path)

    # === 3. Stretch the video to match the audio duration ===
    try:
        video_duration = get_duration(video_path)
        audio_duration = get_duration(audio_file_local)
    except Exception as e:
        raise Exception(str(e))

    stretched_video = "stretched_video.mp4"
    try:
        subprocess.run(
            [sys.executable, "video_stretch.py", video_path, stretched_video,
            str(audio_duration), str(video_duration)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
    except subprocess.CalledProcessError as e:
        # Log detailed diagnostic information.
        logging.error("Video stretching subprocess failed with return code: %s", e.returncode)
        logging.error("stdout: %s", e.stdout)
        logging.error("stderr: %s", e.stderr)
        raise Exception(f"Video stretching failed:\n{e.stdout}\n{e.stderr}")


    # === 4. Add captions from the extracted script into the video ===
    captioned_video = "final_video.mp4"
    try:
        subprocess.run(
            [sys.executable, "video_captions.py", stretched_video, captioned_video, extracted_script_text],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise Exception(f"Adding captions failed:\n{e.output}")

    # # === 5. Add audio to the captioned video ===
    final_video = "final_video.mp4"
    # try:
    #     subprocess.run(
    #         [sys.executable, "audio_insert.py", captioned_video, audio_file_local, final_video],
    #         capture_output=True,
    #         text=True,
    #         encoding="utf-8",
    #         errors="replace",
    #         check=True
    #     )

    # except subprocess.CalledProcessError as e:
    #     logging.error(f"Audio insertion failed:\n{e.output}")
        
    #     raise Exception(f"Audio insertion failed:\n{e.stdout}\n{e.stderr}")
 
    
    shutil.move("final_video.mp4", "output/final_video.mp4")
    
    app.mount("/output", StaticFiles(directory="output"), name="output")

    return {
        "final_video": "http://localhost:8000/output/final_video.mp4",
        "original_video": os.path.abspath(video_path),
        "stretched_video": os.path.abspath(stretched_video),
        "captioned_video": os.path.abspath(captioned_video),
        "audio_file": os.path.abspath(audio_file_local),
        "response_file": os.path.abspath(response_txt_path),
        "python_code_file": os.path.abspath(py_filename),
        "extracted_script": extracted_script_text,
    }

# --- API endpoint ---
@app.post("/generate-video")
async def generate_video(request: TopicRequest):
    topic = request.topic

    # === 1. Call the Wordware API to generate a response (and write response.txt) ===
    APP_ID = "990839b3-d06f-4f3e-a757-a0266057b64d"
    url = f"https://app.wordware.ai/api/released-app/{APP_ID}/run"
    payload = {
        "inputs": {"Topic": topic},
        "version": "^1.0"
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}

    response = requests.post(url, json=payload, headers=headers, stream=True)
    if response.status_code != 200:
        try:
            error_details = response.json()
        except Exception:
            error_details = response.text
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Wordware API request failed: {error_details}"
        )

    all_data = io.StringIO()
    for chunk in response.iter_lines():
        if chunk:  # skip keep-alive chunks
            decoded = chunk.decode("utf-8", errors="replace")
            all_data.write(decoded + "\n")
    response_txt_path = "response.txt"
    with open(response_txt_path, "w", encoding="utf-8") as f:
        f.write(all_data.getvalue())

    try:
        result = process_response_file(response_txt_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
