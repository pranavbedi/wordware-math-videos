import sys
import traceback
import ffmpeg

def stretch_video(input_file, output_file, longer_duration, shorter_duration):
    """
    Stretches the video so that its duration becomes the specified longer duration.
    
    Parameters:
      input_file (str): Path to the input video file.
      output_file (str): Path to the output (stretched) video file.
      longer_duration (float): The target (longer) duration (e.g., the audio length).
      shorter_duration (float): The original (shorter) video duration.
    """
    try:
        # Calculate the slowdown factor.
        slowdown_factor = float(longer_duration) / float(shorter_duration)
        print(f"Using slowdown factor: {slowdown_factor}")

        # Load the input video.
        inp = ffmpeg.input(input_file)
        
        # Apply the setpts filter to stretch the video timing.
        v = inp.video.filter('setpts', f'PTS*{slowdown_factor}')
        
        # Run the ffmpeg command and capture output.
        ffmpeg.output(v, output_file, vcodec='libx264') \
              .overwrite_output() \
              .run(capture_stdout=True, capture_stderr=True)
        
    except ffmpeg.Error as e:
        print("FFmpeg error occurred:", file=sys.stderr)
        # Print detailed ffmpeg error output.
        print(e.stderr.decode('utf-8'), file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)  # Exit with error so the subprocess returns a non-zero exit code.
        
    except Exception as e:
        print("An unexpected error occurred:", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python video_stretch.py <input_file> <output_file> <longer_duration> <shorter_duration>")
        print("Example: python video_stretch.py input.mp4 output_slow.mp4 37 15")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    longer_duration = sys.argv[3]
    shorter_duration = sys.argv[4]
    
    stretch_video(input_file, output_file, longer_duration, shorter_duration)
