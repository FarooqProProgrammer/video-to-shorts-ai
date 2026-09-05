import os
import json
from openai import OpenAI

def analyze_content(transcript: dict) -> list:
    """Analyzes the transcript using an LLM to find the best segments."""
    print("Analyzing transcript to find engaging segments...")
    
    base_url = os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1")
    api_key = os.getenv("OPENAI_API_KEY", "dummy")
    model_name = os.getenv("LLM_MODEL", "phi3")
    
    client = OpenAI(base_url=base_url, api_key=api_key)
    
    # Calculate video duration in seconds
    duration = 0
    if transcript["segments"]:
        duration = transcript["segments"][-1]["end"]
        
    # Request 1 short for roughly every 4 minutes, with a minimum of 3
    num_shorts = max(3, int((duration / 60) / 4))
    
    system_prompt = (
        "You are an expert video editor and social media manager. "
        f"Find the {num_shorts} most engaging, viral-worthy segments from this video transcript. "
        "Each segment should be 30-60 seconds long. "
        "Return the result ONLY as a JSON list of objects, where each object has 'start' (float), 'end' (float), and 'reason' (string) fields."
    )
    
    user_prompt = "Here is the transcript:\n\n"
    for seg in transcript["segments"]:
        user_prompt += f"[{seg['start']:.2f} - {seg['end']:.2f}]: {seg['text']}\n"
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        
        # Parse JSON from the response (handling potential markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        segments = json.loads(content)
        return segments
    except Exception as e:
        print(f"Error during LLM analysis: {e}")
        raise Exception(f"LLM API Error: {str(e)}")
