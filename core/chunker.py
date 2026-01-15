import logging
import soundfile as sf
import numpy as np
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class AudioChunker:
    """Smart audio chunking for transcription."""
    
    def __init__(self, chunk_length=30, overlap=5, sample_rate=16000):
        """
        Initialize chunker.
        
        Args:
            chunk_length: Duration of each chunk in seconds
            overlap: Overlap between chunks in seconds
            sample_rate: Audio sample rate
        """
        self.chunk_length = chunk_length
        self.overlap = overlap
        self.sample_rate = sample_rate
        self.chunk_samples = chunk_length * sample_rate
        self.overlap_samples = overlap * sample_rate
    
    def load_audio(self, audio_path):
        """Load audio file."""
        try:
            audio, sr = sf.read(audio_path, dtype=np.float32)
            
            # Convert stereo to mono
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
            
            return audio.astype(np.float32), sr
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise
    
    def chunk_audio(self, audio):
        """
        Split audio into chunks with overlap.
        
        Returns:
            List of audio chunks
        """
        chunks = []
        step = self.chunk_samples - self.overlap_samples
        
        start = 0
        while start < len(audio):
            end = min(start + self.chunk_samples, len(audio))
            chunk = audio[start:end]
            chunks.append(chunk)
            
            if end == len(audio):
                break
            
            start += step
        
        return chunks
    
    def save_chunks(self, audio_path, output_dir="./chunks"):
        """
        Load audio and save chunks to disk.
        
        Returns:
            List of chunk file paths
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            audio, sr = self.load_audio(audio_path)
            
            # Resample if needed
            if sr != self.sample_rate:
                from scipy import signal
                num_samples = int(len(audio) * self.sample_rate / sr)
                audio = signal.resample(audio, num_samples)
            
            chunks = self.chunk_audio(audio)
            
            chunk_paths = []
            for i, chunk in enumerate(chunks):
                chunk_path = os.path.join(output_dir, f"chunk_{i:04d}.wav")
                sf.write(chunk_path, chunk, self.sample_rate)
                chunk_paths.append(chunk_path)
            
            logger.info(f"Created {len(chunk_paths)} chunks from audio")
            return chunk_paths
            
        except Exception as e:
            logger.error(f"Error chunking audio: {e}")
            raise
    
    def get_chunk_duration(self, chunk):
        """Get duration of a chunk in seconds."""
        return len(chunk) / self.sample_rate
    
    def merge_chunks(self, chunks):
        """Merge chunks back into single audio array."""
        if not chunks:
            return np.array([])
        
        # Remove overlap regions when merging
        merged = chunks[0].copy()
        
        for chunk in chunks[1:]:
            # Skip overlap_samples from the start of subsequent chunks
            merged = np.concatenate([merged, chunk[self.overlap_samples:]])
        
        return merged
    
    def cleanup_chunks(self, chunk_dir="./chunks"):
        """Remove temporary chunk directory."""
        try:
            import shutil
            if os.path.exists(chunk_dir):
                shutil.rmtree(chunk_dir)
                logger.info("Chunk directory cleaned up")
        except Exception as e:
            logger.warning(f"Could not cleanup chunks: {e}")
