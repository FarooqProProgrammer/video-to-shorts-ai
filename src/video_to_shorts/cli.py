import argparse
import sys
import os
from dotenv import load_dotenv

# Add the 'src' directory to the Python path so absolute imports work when run as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from video_to_shorts.core.downloader import download_video
from video_to_shorts.core.transcriber import transcribe_video
from video_to_shorts.core.analyzer import analyze_content
from video_to_shorts.core.editor import create_shorts

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Long Video to Shorts AI CLI")
    parser.add_argument("url", help="YouTube URL of the long video")
    args = parser.parse_args()
    
    url = args.url
    print(f"Starting process for: {url}")
    
    # 1. Download
    video_path = download_video(url)
    
    # 2. Transcribe
    transcript = transcribe_video(video_path)
    print("\n--- Transcription Complete ---")
    print(f"Total Text Length: {len(transcript['text'])} characters.")
    print("------------------------------\n")
    
    # 3. Analyze
    segments = analyze_content(transcript)
    print("\n--- Content Analysis Complete ---")
    import json
    print(json.dumps(segments, indent=2))
    print("---------------------------------\n")
    
    # 4. Generate Shorts
    shorts = create_shorts(video_path, segments)
    
    print(f"Successfully created shorts: {shorts}")

if __name__ == "__main__":
    main()
