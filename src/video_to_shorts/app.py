import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Add the 'src' directory to the Python path so absolute imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from video_to_shorts.core.downloader import download_video
from video_to_shorts.core.transcriber import transcribe_video
from video_to_shorts.core.analyzer import analyze_content
from video_to_shorts.core.editor import create_shorts

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Video to Shorts AI", page_icon="🎬", layout="centered")

# --- SIDEBAR: TESTING & SETTINGS ---
with st.sidebar:
    st.header("🔧 Settings & Testing")
    st.markdown("Use this button to test if your local AI model (Ollama/OpenAI) is connected and responding correctly, without having to download a full video.")
    if st.button("Test AI Connection"):
        with st.spinner("Sending test prompt to AI..."):
            dummy_transcript = {
                "segments": [
                    {"start": 0.0, "end": 15.0, "text": "Welcome to my video today we are talking about artificial intelligence."},
                    {"start": 15.0, "end": 30.0, "text": "AI is completely changing the world because it automates extremely boring tasks."},
                    {"start": 30.0, "end": 45.0, "text": "In the future, AI will help us explore space and cure diseases."},
                    {"start": 45.0, "end": 60.0, "text": "If you enjoyed this quick video, hit the like button and subscribe for more!"}
                ]
            }
            try:
                result = analyze_content(dummy_transcript)
                st.success("✅ AI is working perfectly!")
                st.json(result)
            except Exception as e:
                st.error(f"❌ AI Test Failed: {e}")

st.title("🎬 AI Long Video to Shorts Maker")
st.markdown("Convert long YouTube videos into engaging vertical shorts using AI!")

# --- UI TABS ---
tab1, tab2 = st.tabs(["📺 Download from YouTube", "📁 Use Existing Downloaded Video"])

url = None
selected_file = None
start_processing = False

with tab1:
    url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
    if st.button("Generate from URL", type="primary"):
        if not url:
            st.error("Please enter a YouTube URL.")
        else:
            start_processing = True

with tab2:
    import glob
    existing_files = glob.glob("downloads/*.mp4") + glob.glob("downloads/*.mkv") + glob.glob("downloads/*.webm")
    if existing_files:
        selected_file = st.selectbox("Select a previously downloaded video:", existing_files)
        if st.button("Generate from Selected File", type="primary"):
            start_processing = True
    else:
        st.info("No previously downloaded videos found in the 'downloads/' folder.")

if start_processing:
    with st.status("Processing your video... (This takes time on a CPU)", expanded=True) as status:
        try:
            video_path = None
            
            # 1. DOWNLOAD STEP
            if url and not selected_file:
                st.write("📥 Downloading video...")
                download_progress = st.progress(0.0, text="Starting download...")
                
                def dl_callback(percent, eta):
                    download_progress.progress(percent, text=f"Downloading... {int(percent*100)}% (ETA: {eta})")
                    
                video_path = download_video(url, progress_callback=dl_callback)
                download_progress.progress(1.0, text="Download complete!")
            else:
                video_path = selected_file
                st.write(f"📥 Using existing video: {video_path}")
            
            # 2. TRANSCRIPTION STEP
            st.write("📝 Transcribing audio (this will take time)...")
            transcribe_progress = st.progress(0.0, text="Loading AI model...")
            
            def ts_callback(percent, latest_text):
                # Show the latest transcribed text in the progress bar
                transcribe_progress.progress(percent, text=f"Transcribing: {latest_text}")
                
            transcript = transcribe_video(video_path, progress_callback=ts_callback)
            transcribe_progress.progress(1.0, text="Transcription complete!")
            st.write(f"✅ Transcription complete! Length: {len(transcript['text'])} characters.")
            
            # 3. ANALYSIS STEP
            st.write("🧠 Analyzing content with AI...")
            segments = analyze_content(transcript)
            st.write(f"✅ Found {len(segments)} engaging segments.")
            
            # 4. CROPPING STEP
            st.write("✂️ Cropping and generating short videos...")
            shorts = create_shorts(video_path, segments)
            
            status.update(label="Process complete!", state="complete", expanded=False)
            
            st.success(f"Successfully generated {len(shorts)} shorts!")
            
            # Display the videos in columns
            st.subheader("Your Generated Shorts")
            cols = st.columns(3)
            for i, short_path in enumerate(shorts):
                with cols[i % 3]:
                    st.video(short_path)
                    with open(short_path, "rb") as file:
                        st.download_button(
                            label=f"Download Short {i+1}",
                            data=file,
                            file_name=os.path.basename(short_path),
                            mime="video/mp4"
                        )
                    
        except Exception as e:
            status.update(label="An error occurred", state="error")
            st.error(f"Error: {str(e)}")
