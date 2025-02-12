import sys
import re
import logging
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.config import change_settings

change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

FFMPEG_BINARY = os.getenv('FFMPEG_BINARY', 'ffmpeg-imageio')
IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

def get_duration(file_path: str) -> float:
    """
    Returns the duration (in seconds) of the given video file.
    """
    try:
        clip = VideoFileClip(file_path)
        logging.info(f"{file_path}: Duration Found")
        return clip.duration
    except Exception as e:
        raise Exception(f"Failed to get duration for {file_path}: {e}")

def split_paragraph_into_sentences(paragraph):
    """
    Split a paragraph into sentences.
    This regex splits on a period, exclamation point, or question mark,
    followed by whitespace.
    """
    sentences = re.split(r'(?<=[.!?])\s+', paragraph.strip())
    return [s for s in sentences if s]

def build_text_clips(sentences, video_duration):
    """
    Using MoviePy, build a list of TextClips for each sentence.
    Each sentence is displayed for an equal portion of the video duration.
    """
    num_sentences = len(sentences)
    if num_sentences == 0:
        return []
    
    caption_duration = video_duration / num_sentences
    clips = []
    
    # Set a width for the text clip (adjust as needed for your video)
    clip_width = 800
    
    for i, sentence in enumerate(sentences):
        start_time = i * caption_duration
        
        txt_clip = TextClip(
            sentence,
            fontsize=30,           # Adjust fontsize as needed
            color='white',
            font='ProximaNova-Bold',  # Use your bold font (or full path if needed)
            method='caption',      # Use the Pillow-based method
            size=(clip_width, None),
            align='center'
        )
        txt_clip = txt_clip.set_position(('center', 'bottom')) \
                           .set_start(start_time) \
                           .set_duration(caption_duration)
        clips.append(txt_clip)
    
    return clips

def main():
    if len(sys.argv) < 4:
        print("Usage: python video_captions.py <input_video> <output_video> <script_paragraph>")
        sys.exit(1)
    
    input_video = sys.argv[1]
    output_video = sys.argv[2]
    paragraph = sys.argv[3]
    
    # Get video duration (in seconds)
    video_duration = get_duration(input_video)
    print("Video duration:", video_duration)
    
    # Split the paragraph into sentences
    sentences = split_paragraph_into_sentences(paragraph)
    print("Sentences:", sentences)
    
    # Build text clips for the captions using MoviePy
    text_clips = build_text_clips(sentences, video_duration)
    
    # Load the original video clip
    video_clip = VideoFileClip(input_video)
    
    # Create the composite clip with the video and text overlays
    final_clip = CompositeVideoClip([video_clip] + text_clips, size=video_clip.size)
    
    # Load the external audio
    audio_clip = AudioFileClip("downloaded_audio.mp3")
    
    if audio_clip.duration > video_clip.duration:
        audio_clip = audio_clip.subclip(0, video_clip.duration)

    print("Audio duration:", audio_clip.duration)
    
    # Set the external audio on the final clip
    final_clip = final_clip.set_audio(audio_clip)
    
    # Write the final video to file, specifying an audio bitrate and temporary audio file
    try:
        final_clip.write_videofile(
            output_video,
            codec="libx264",
            audio_codec="aac",
            audio_bitrate="192k",
            temp_audiofile="temp-audio.m4a",
            remove_temp=False
       )
    except Exception as e:
        print("❌ ERROR: Failed to write final video!")
        print("🔍 Exception Message:", str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)  # Exit with error code

if __name__ == "__main__":
    main()
