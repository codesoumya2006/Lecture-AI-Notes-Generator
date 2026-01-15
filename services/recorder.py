import logging
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
import threading
import time

logger = logging.getLogger(__name__)

class AudioRecorder:
    """Live audio recording service."""
    
    def __init__(self, sample_rate=16000, channels=1, output_dir="./recordings"):
        """
        Initialize recorder.
        
        Args:
            sample_rate: Recording sample rate
            channels: Number of audio channels (1 for mono)
            output_dir: Directory to save recordings
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.output_dir = output_dir
        self.is_recording = False
        self.recording_data = []
        self.stream = None
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def list_devices(self):
        """List available audio devices."""
        try:
            devices = sd.query_devices()
            return devices
        except Exception as e:
            logger.error(f"Error listing devices: {e}")
            return []
    
    def start_recording(self, device=None):
        """
        Start recording audio.
        
        Args:
            device: Device index (None = default)
        """
        if self.is_recording:
            logger.warning("Recording already in progress")
            return
        
        try:
            logger.info("Starting recording...")
            self.is_recording = True
            self.recording_data = []
            
            def audio_callback(indata, frames, time_info, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")
                # Store data as float32
                self.recording_data.append(indata.copy())
            
            self.stream = sd.InputStream(
                device=device,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=audio_callback,
                blocksize=16000,  # 1 second blocks at 16kHz
                dtype=np.float32
            )
            
            self.stream.start()
            logger.info("✓ Recording started")
        
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            self.is_recording = False
            raise
    
    def stop_recording(self) -> str:
        """
        Stop recording and save audio file.
        
        Returns:
            Path to saved audio file
        """
        if not self.is_recording:
            logger.warning("No recording in progress")
            return ""
        
        try:
            logger.info("Stopping recording...")
            
            if self.stream:
                self.stream.stop()
                self.stream.close()
            
            self.is_recording = False
            
            # Concatenate all recorded chunks
            if not self.recording_data:
                logger.warning("No audio data recorded")
                return ""
            
            audio_data = np.concatenate(self.recording_data, axis=0)
            
            # Generate filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = str(Path(self.output_dir) / f"recording_{timestamp}.wav")
            
            # Save audio file
            sf.write(output_path, audio_data, self.sample_rate)
            
            logger.info(f"✓ Recording saved: {output_path}")
            logger.info(f"Duration: {len(audio_data) / self.sample_rate:.1f} seconds")
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            self.is_recording = False
            raise
    
    def get_duration(self):
        """Get duration of current recording in seconds."""
        if not self.recording_data:
            return 0
        
        total_samples = sum(len(chunk) for chunk in self.recording_data)
        return total_samples / self.sample_rate
    
    def cleanup_recordings(self):
        """Delete all recordings."""
        try:
            import shutil
            if Path(self.output_dir).exists():
                shutil.rmtree(self.output_dir)
                Path(self.output_dir).mkdir(parents=True, exist_ok=True)
                logger.info("Cleaned up all recordings")
        except Exception as e:
            logger.warning(f"Could not cleanup recordings: {e}")
