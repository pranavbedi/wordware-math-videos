# Wordware POC - ReadMe

## Overview
This project is a proof-of-concept (PoC) application that utilizes the Wordware API to generate animated educational videos from textual input. The application is designed with the idea that people learn best with quick 60-75 second videos, similar to those found on TikTok and Reels. Since Wordware does not currently support video output or execution of the Manim Python library, these tasks are handled locally.

## Features
- Accepts user-inputted topics via a web interface.
- Uses the Wordware API to generate Manim animation scripts.
- Extracts, processes, and repairs generated animation code.
- Downloads and synchronizes audio files with animations.
- Stretches video durations to match audio lengths.
- Adds captions and finalizes the generated videos.
- Future improvements include adding if-statements to the Wordware app to support different modes, such as promotional content.

## How Wordware is Used
Wordware plays a critical role in the automation of educational video creation:
1. **Script Generation** - The user inputs a topic, which is passed to Wordware to generate a structured script using Gemini 2.0 Flash.
2. **Prompt Creation** - The generated script is then transformed into a detailed prompt that guides the generation of a Manim animation script.
3. **Code Generation** - Using models like OpenAI’s `o3-mini`, Wordware generates the Python script necessary for creating the animation in Manim.
4. **Error Handling and Repairs** - Certain problematic Manim components that cause execution issues are identified and fixed dynamically to ensure compatibility across different systems.
5. **Voice Generation** - The script is cleaned up, removing unnecessary references to visuals, and then processed through 11 Labs AI to generate a natural-sounding voice-over.
6. **Final Processing** - The backend extracts the necessary Python animation script, runs it through Manim, synchronizes the output with the generated voice-over, stretches the video to align with the audio, and overlays captions before finalizing the video.

## Technologies Used
### Backend (FastAPI)
- **FastAPI**: Handles API requests and processes video generation.
- **Wordware API**: Used to generate scripts, prompts, and refine animation scripts.
- **FFmpeg**: Extracts video/audio durations.
- **Pydantic**: Defines request models.
- **Requests**: Handles API calls.
- **Subprocess**: Runs external Python scripts.

### Frontend (React)
- **React.js**: Provides the user interface.
- **State Management**: Handles video generation states.
- **CSS Modules**: Styles UI components.

## Installation
### Backend Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/wordware-poc.git
   cd video-maker
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Create a `.env` file in the backend directory and add:
     ```env
     API_KEY=your_wordware_api_key
     ```

### Frontend Setup
1. Navigate to the frontend folder:
   ```sh
   cd ../frontend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the frontend:
   ```sh
   npm start
   ```

## Running the Application
### Start the Backend Server
```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
### Start the Frontend
```sh
npm start
```
### Access the Web Interface
Open a browser and navigate to:
```
http://localhost:3000
```

## API Endpoints
### Generate Video
- **Endpoint:** `POST /generate-video`
- **Request Body:**
  ```json
  {
    "topic": "Introduction to Derivatives"
  }
  ```
- **Response:**
  ```json
  {
    "final_video": "http://localhost:8000/output/final_video.mp4",
    "original_video": "path/to/original.mp4",
    "stretched_video": "path/to/stretched.mp4",
    "captioned_video": "path/to/captioned.mp4",
    "audio_file": "path/to/audio.mp3",
    "response_file": "path/to/response.txt",
    "python_code_file": "path/to/generated_manim.py",
    "extracted_script": "Extracted script text"
  }
  ```

## Demo and Sample Output
- **Recorded Demo:** [Insert link to demo video]
- **Sample Output Video:** [Insert link to final generated video]

## My Work with Wordware
- **Overview:** This project demonstrates the integration of Wordware with video generation, leveraging AI to create highly dynamic and engaging educational videos. By automating script and animation generation, it significantly reduces the effort required to produce content.
- **Link to Wordware Work:** [Insert link to Wordware-related projects or documentation]

## Future Improvements
- Implement conditional generation modes (e.g., promotional content).
- Support additional animation styles.
- Improve error handling and diagnostics.
- Deploy to cloud for scalability.

## License
MIT License - Free to use and modify.

