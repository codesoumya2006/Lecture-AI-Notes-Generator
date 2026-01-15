import hashlib
import os

def get_unique_audio_path(youtube_url: str) -> str:
    url_hash = hashlib.md5(youtube_url.encode()).hexdigest()
    return os.path.join("downloads", f"audio_{url_hash}.wav")
