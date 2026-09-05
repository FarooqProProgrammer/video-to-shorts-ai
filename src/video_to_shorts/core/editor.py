import os
import cv2
import mediapipe as mp
from moviepy import VideoFileClip

def get_face_center(frame):
    """Uses Mediapipe to detect a face in the frame and returns its X center coordinate."""
    mp_face_detection = mp.solutions.face_detection
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        # Convert BGR (OpenCV) to RGB (Mediapipe)
        results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.detections:
            # Use the first detected face
            bbox = results.detections[0].location_data.relative_bounding_box
            h, w, _ = frame.shape
            x_center = int((bbox.xmin + bbox.width / 2) * w)
            return x_center
    return None

def create_shorts(video_path: str, segments: list) -> list:
    """Crops the video into 9:16 vertical shorts based on the identified segments."""
    print(f"Creating {len(segments)} shorts...")
    os.makedirs("output", exist_ok=True)
    generated_files = []
    
    for i, seg in enumerate(segments):
        start_time = seg.get('start', 0)
        end_time = seg.get('end', 0)
        
        if end_time <= start_time:
            print(f"Invalid segment times: {start_time} to {end_time}. Skipping.")
            continue
            
        print(f"Processing segment {i+1}: {start_time}s to {end_time}s")
        try:
            clip = VideoFileClip(video_path).subclip(start_time, end_time)
            
            w, h = clip.size
            target_w = int(h * 9 / 16) # 9:16 aspect ratio width
            
            # To save CPU cycles, we'll find the face in the middle frame of the clip
            # instead of tracking it frame-by-frame, which is extremely slow on CPU.
            middle_time = (end_time - start_time) / 2
            frame = clip.get_frame(middle_time)
            
            face_x = get_face_center(frame)
            if face_x is None:
                print("No face detected, defaulting to center crop.")
                face_x = w // 2
                
            # Calculate crop coordinates keeping the face centered
            x1 = max(0, face_x - target_w // 2)
            x2 = min(w, x1 + target_w)
            
            # Adjust boundaries if the face is too close to an edge
            if x2 == w:
                x1 = w - target_w
            if x1 == 0:
                x2 = target_w
                
            cropped_clip = clip.crop(x1=x1, y1=0, x2=x2, y2=h)
            
            output_path = os.path.join("output", f"short_{i+1}.mp4")
            
            # Write the video file (CPU encoding)
            cropped_clip.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac", 
                logger=None # Suppress moviepy progress bar to keep CLI clean
            )
            
            generated_files.append(output_path)
            
            # Clean up
            cropped_clip.close()
            clip.close()
            print(f"Finished {output_path}")
            
        except Exception as e:
            print(f"Error creating short {i+1}: {e}")
            
    return generated_files
