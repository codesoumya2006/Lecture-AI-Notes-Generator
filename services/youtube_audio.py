import os
import yt_dlp

def download_audio(youtube_url: str, output_path: str):
    if os.path.exists(output_path):
        os.remove(output_path)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path.replace(".wav", ""),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
