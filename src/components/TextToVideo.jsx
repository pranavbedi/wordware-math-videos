import React, { useState } from 'react';
import './TextToVideo.css';
import preview1 from '../assets/preview1.png';
import preview2 from '../assets/preview2.png';
import preview3 from '../assets/preview3.png';
import audioWave from '../assets/audio.png';

function TextToVideo() {
  // Local state
  const [selectedPreview, setSelectedPreview] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [finalVideoUrl, setFinalVideoUrl] = useState(null);
  const [error, setError] = useState("");

  // Handle clicking on a small preview image
  const handlePreviewClick = (image) => {
    setSelectedPreview(image);
  };

  // Handle the Generate button click: call the backend
  const handleGenerate = async () => {
    setIsLoading(true);
    setError("");
    setFinalVideoUrl(null);

    // The backend endpoint URL – adjust if needed (e.g., deployed URL)
    const endpoint = "http://localhost:8000/generate-video";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        // Only the prompt is used as the topic; the video type is ignored.
        body: JSON.stringify({ topic: prompt })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error generating video");
      }

      const data = await response.json();
      // The backend returns a JSON object with a key "final_video"
      setFinalVideoUrl(data.final_video);
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="text-to-video">
      <div className="text-to-video-container">
        {/* Left Card: Form */}
        <div className="text-to-video-card left-card">
          <h2>
            <span className="icon-purple">★</span> Turn your Text into 
            <span className="text-purple"> Video</span>
          </h2>

          <div className="form-group">
            <label htmlFor="videoType">Select video type</label>
            <select id="videoType" name="videoType">
              <option value="">I want Explainer Videos</option>
              <option value="promo">Promo Videos</option>
              <option value="tutorial">Tutorial Videos</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="videoPrompt">What topic would you like to generate a video for?</label>
            <textarea
              id="videoPrompt"
              name="videoPrompt"
              rows="4"
              placeholder="Tangents vs Derivatives"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            ></textarea>
          </div>

          <button 
            className="btn btn-generate" 
            onClick={handleGenerate}
            disabled={isLoading || prompt.trim() === ""}
          >
            {isLoading ? "Generating..." : "Generate"}
          </button>

          {error && <p className="error-message">{error}</p>}
        </div>

        {/* Right Card: Previews, Waveform or Final Video */}
        <div className="text-to-video-card right-card">
          {/* If a final video URL exists, show the video player */}
          {finalVideoUrl ? (
                <div className="video-container">
                    <video controls src={finalVideoUrl} className="final-video" />
                </div>
          ) : (
            <>
              {/* Small preview images at the top */}
              <div className="preview-images">
                <img 
                  src={preview1} 
                  alt="Preview 1" 
                  onClick={() => handlePreviewClick(preview1)}
                />
                <img 
                  src={preview2} 
                  alt="Preview 2" 
                  onClick={() => handlePreviewClick(preview2)}
                />
                <img 
                  src={preview3} 
                  alt="Preview 3" 
                  onClick={() => handlePreviewClick(preview3)}
                />
              </div>

              {/* If an image is selected, show it large. Otherwise show the audio waveform */}
              <div className="audio-waveform">
                {selectedPreview ? (
                  <img 
                    className="expanded-preview" 
                    src={selectedPreview} 
                    alt="Selected Preview" 
                  />
                ) : (
                  <img 
                    src={audioWave} 
                    alt="Audio Waveform" 
                  />
                )}
              </div>
            </>
          )}

          {/* Vertical toolbar on the right */}
          <div className="vertical-toolbar">
            <button className="toolbar-btn">🔊</button>
            <button className="toolbar-btn">⚙</button>
            <button className="toolbar-btn">🎵</button>
            <button className="toolbar-btn">✎</button>
          </div>
        </div>
      </div>
    </section>
  );
}

export default TextToVideo;
