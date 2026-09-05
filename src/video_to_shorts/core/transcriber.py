from faster_whisper import WhisperModel

def transcribe_video(video_path: str, progress_callback=None) -> dict:
    """Transcribes the video using faster-whisper and returns a dictionary with timestamps."""
    print(f"Transcribing {video_path}...")
    
    # Using 'base' or 'small' model since we are running on CPU
    model_size = "small"
    
    # Configure for CPU execution with int8 quantization for performance
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    segments, info = model.transcribe(video_path, beam_size=5)
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    
    transcript_segments = []
    full_text = ""
    for segment in segments:
        segment_data = {
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        }
        transcript_segments.append(segment_data)
        full_text += segment.text + " "
        
        if progress_callback and info.duration > 0:
            # Calculate progress based on the current timestamp vs total duration
            progress = min(segment.end / info.duration, 1.0)
            progress_callback(progress, segment.text)
        
    return {"text": full_text.strip(), "segments": transcript_segments}
