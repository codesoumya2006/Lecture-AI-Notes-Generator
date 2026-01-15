import logging
import os
import subprocess
from pathlib import Path
import yt_dlp

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """Download audio from YouTube videos."""
    
    def __init__(self, output_dir="./downloads"):
        """
        Initialize downloader.
        
        Args:
            output_dir: Directory to save downloaded audio files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def download_audio(self, youtube_url: str, audio_format="m4a"):
        """
        Download audio from YouTube URL.
        
        Args:
            youtube_url: YouTube video URL
            audio_format: Audio format (m4a, mp3, wav, etc.)
        
        Returns:
            Path to downloaded audio file
        """
        try:
            logger.info(f"Downloading audio from: {youtube_url}")
            
            # Try with FFmpeg postprocessing first, fall back to raw download
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': 30,
                'socket_blocking_timeout': 30
            }
            
            # Try to use FFmpeg if available
            try:
                import shutil
                if shutil.which('ffmpeg'):
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': audio_format,
                        'preferredquality': '192',
                    }]
            except:
                pass  # Continue without FFmpeg postprocessing
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                filename = ydl.prepare_filename(info)
                logger.info(f"Downloaded file: {filename}")
                
                # Check if postprocessing created the target format
                base_path = os.path.splitext(filename)[0]
                audio_path = f"{base_path}.{audio_format}"
                
                if os.path.exists(audio_path):
                    logger.info(f"✓ Downloaded and converted: {audio_path}")
                    return audio_path
                elif os.path.exists(filename):
                    # Return the raw downloaded file (might be webm, m4a, etc.)
                    logger.info(f"✓ Downloaded (raw format): {filename}")
                    return filename
                else:
                    # Try to find the file by pattern
                    for file in os.listdir(self.output_dir):
                        if os.path.basename(base_path) in file:
                            audio_path = os.path.join(self.output_dir, file)
                            logger.info(f"✓ Downloaded: {audio_path}")
                            return audio_path
                
                raise Exception("Could not find downloaded file")
            
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            raise
    
    def get_video_info(self, youtube_url: str) -> dict:
        """
        Get video metadata without downloading.
        
        Args:
            youtube_url: YouTube video URL
        
        Returns:
            Dict with video title, duration, uploader, etc.
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 30
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'upload_date': info.get('upload_date', ''),
                }
        
        except Exception as e:
            logger.error(f"Error fetching video info: {e}")
            return {}
    
    def cleanup_download(self, file_path: str):
        """Delete downloaded file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.warning(f"Could not delete file: {e}")
    
    def cleanup_all(self):
        """Delete all downloaded files."""
        try:
            import shutil
            if os.path.exists(self.output_dir):
                shutil.rmtree(self.output_dir)
                os.makedirs(self.output_dir, exist_ok=True)
                logger.info("Cleaned up all downloads")
        except Exception as e:
            logger.warning(f"Could not cleanup downloads: {e}")
