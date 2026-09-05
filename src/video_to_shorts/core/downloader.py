import yt_dlp
import os

def download_video(url: str, progress_callback=None) -> str:
    """Downloads the video using yt-dlp and returns the path to the downloaded file."""
    print(f"Downloading video from {url}...")
    
    # Ensure downloads directory exists
    os.makedirs("downloads", exist_ok=True)
    
    def my_hook(d):
        if d['status'] == 'downloading' and progress_callback:
            # Extract percentage string, remove ANSI escape codes if any, and convert to float
            p_str = d.get('_percent_str', '0%').replace('%', '').strip()
            # Handle ANSI escape codes that yt-dlp sometimes adds
            import re
            p_str = re.sub(r'\x1b\[[0-9;]*m', '', p_str)
            try:
                progress_callback(float(p_str) / 100.0, d.get('_eta_str', 'Unknown'))
            except Exception:
                pass
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'progress_hooks': [my_hook] if progress_callback else []
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        # Handle cases where the actual downloaded filename might differ slightly due to merging
        filename = ydl.prepare_filename(info_dict)
        # Check if a merged file (e.g. .mkv) was created instead of .mp4, though we requested mp4
        if not os.path.exists(filename):
            base, _ = os.path.splitext(filename)
            for ext in ['.mp4', '.mkv', '.webm']:
                if os.path.exists(base + ext):
                    filename = base + ext
                    break
                    
        print(f"Downloaded to: {filename}")
        return filename
