// src/services/aiService.js
export async function generateVideo(topic) {
    const response = await fetch("http://localhost:8000/generate-video", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ topic })
    });
  
    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Failed to generate video: ${errorMessage}`);
    }
  
    const data = await response.json();
    return data.video_path;
  }
  