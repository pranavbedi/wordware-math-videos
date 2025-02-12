import sys
import ffmpeg

def combine_video_audio(video_file, audio_file, output_file):
    """
    Combines a video file with an audio file using FFmpeg.
    
    Parameters:
        video_file (str): Path to the input video file (e.g. an MP4 file).
        audio_file (str): Path to the input audio file (e.g. an MP3 file).
        output_file (str): Path to the output video file with combined audio.
    """
    # Load the video and audio inputs
    video = ffmpeg.input(video_file)
    audio = ffmpeg.input(audio_file)
    
    # Combine the inputs:
    # - vcodec="copy" copies the video stream without re-encoding.
    # - acodec="aac" encodes the audio stream to AAC.
    # - shortest=None passes the '-shortest' flag so the output stops when the shortest stream ends.
    (
        ffmpeg
        .output(video, audio, output_file, vcodec="copy", acodec="aac", shortest=None)
        .overwrite_output()
        .run()
    )

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python audio_insert.py <video_file> <audio_file> <output_file>")
        sys.exit(1)
    
    video_file = sys.argv[1]
    audio_file = sys.argv[2]
    output_file = sys.argv[3]
    
    combine_video_audio(video_file, audio_file, output_file)
