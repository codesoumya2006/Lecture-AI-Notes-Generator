import logging
import numpy as np
from pathlib import Path
import subprocess
import json

logger = logging.getLogger(__name__)

class FastTranscriber:
    """Fast transcription using OpenAI Whisper (fallback) or faster-whisper."""
    
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        """
        Initialize Whisper model.
        
        Args:
            model_size: tiny, base, small, medium, large
            device: cpu or cuda
            compute_type: int8 (fastest), float16, float32
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        self.model_type = None
        
        logger.info(f"Loading Whisper model: {model_size}")
        
        # Try faster-whisper first (faster)
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                download_root="./models"
            )
            self.model_type = "faster-whisper"
            logger.info("✓ Using faster-whisper model")
        except ImportError:
            logger.warning("faster-whisper not available, trying OpenAI Whisper...")
            # Fallback to OpenAI Whisper
            try:
                import whisper
                self.model = whisper.load_model(model_size, device=device)
                self.model_type = "openai-whisper"
                logger.info("✓ Using OpenAI Whisper model")
            except Exception as e:
                logger.warning(f"OpenAI Whisper also failed: {e}")
                self.model = None
                self.model_type = None
        except Exception as e:
            logger.error(f"Error loading faster-whisper: {e}")
            # Try fallback
            try:
                import whisper
                self.model = whisper.load_model(model_size, device=device)
                self.model_type = "openai-whisper"
                logger.info("✓ Using OpenAI Whisper (fallback)")
            except Exception as e2:
                logger.error(f"All transcription models failed: {e2}")
                self.model = None
                self.model_type = None
    
    def transcribe(self, audio_path, language="en", beam_size=1):
        """
        Transcribe audio file.
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en', 'es', 'fr')
            beam_size: Beam search width (1 = fastest, higher = better quality)
        
        Returns:
            Full text transcript
        """
        try:
            import os
            import shutil
            
            logger.info(f"Transcribing with {self.model_type}: {audio_path}")
            
            # Validate file exists
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                # Try to find it by listing directory
                dirname = os.path.dirname(audio_path) or '.'
                if os.path.exists(dirname):
                    files = os.listdir(dirname)
                    logger.info(f"Files in {dirname}: {files}")
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # If filename has special characters or is WebM, handle it
            if any(ord(c) > 127 for c in audio_path) or audio_path.endswith('.webm'):
                logger.info(f"Processing file with special characters or WebM format...")
                base_dir = os.path.dirname(audio_path)
                
                # For WebM, convert to WAV first
                if audio_path.endswith('.webm'):
                    from core.audio_pipeline import AudioPipeline
                    pipeline = AudioPipeline()
                    wav_path = pipeline._convert_webm_to_wav(audio_path)
                    if wav_path and os.path.exists(wav_path):
                        audio_path = wav_path
                        logger.info(f"Using converted WAV: {audio_path}")
                
                # If still has special characters, create a sanitized copy
                if any(ord(c) > 127 for c in audio_path):
                    ext = os.path.splitext(audio_path)[1]
                    safe_name = f"audio_temp{ext}"
                    safe_path = os.path.join(base_dir, safe_name)
                    
                    if not os.path.exists(safe_path):
                        shutil.copy2(audio_path, safe_path)
                        logger.info(f"Created sanitized copy: {safe_path}")
                    
                    audio_path = safe_path
            
            if self.model is None:
                logger.warning("No transcription model available - using fallback")
                return "This is a sample transcription. Please install faster-whisper or whisper for actual audio processing."
            
            # Handle faster-whisper
            if self.model_type == "faster-whisper":
                try:
                    segments, info = self.model.transcribe(
                        audio_path,
                        language=language,
                        beam_size=beam_size,
                        vad_filter=True,
                        vad_parameters={"threshold": 0.6},
                        temperature=0.0,
                        condition_on_previous_text=False
                    )
                    
                    # Collect all segments
                    text = ""
                    for segment in segments:
                        text += segment.text + " "
                    
                    text = text.strip()
                    logger.info(f"Transcription complete ({self.model_type}): {len(text)} characters")
                    return text if text else "[No speech detected in audio]"
                except Exception as e:
                    logger.error(f"faster-whisper transcription failed: {e}")
                    raise
            
            # Handle OpenAI Whisper
            elif self.model_type == "openai-whisper":
                try:
                    result = self.model.transcribe(
                        audio_path,
                        language=language,
                        verbose=False
                    )
                    
                    text = result.get("text", "").strip()
                    logger.info(f"Transcription complete ({self.model_type}): {len(text)} characters")
                    return text if text else "[No speech detected in audio]"
                except Exception as e:
                    logger.error(f"OpenAI Whisper transcription failed: {e}")
                    raise
            
            else:
                logger.error(f"Unknown model type: {self.model_type}")
                raise ValueError(f"Unknown model type: {self.model_type}")
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise
    
    def transcribe_with_timestamps(self, audio_path, language="en", beam_size=1):
        """
        Transcribe audio with word-level timestamps.
        
        Returns:
            List of dicts with 'text' and 'timestamp' keys
        """
        try:
            logger.info(f"Transcribing with timestamps: {audio_path}")
            
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=beam_size,
                vad_filter=True,
                temperature=0.0,
                condition_on_previous_text=False
            )
            
            results = []
            for segment in segments:
                results.append({
                    "text": segment.text.strip(),
                    "start": segment.start,
                    "end": segment.end,
                    "id": segment.id
                })
            
            logger.info(f"Transcription complete: {len(results)} segments")
            return results
            
        except Exception as e:
            logger.error(f"Error during timestamped transcription: {e}")
            raise
    
    def batch_transcribe(self, audio_paths, language="en", beam_size=1):
        """
        Transcribe multiple files sequentially.
        
        Args:
            audio_paths: List of audio file paths
            language: Language code
            beam_size: Beam search width
        
        Returns:
            List of transcripts
        """
        transcripts = []
        for audio_path in audio_paths:
            try:
                text = self.transcribe(audio_path, language, beam_size)
                transcripts.append(text)
            except Exception as e:
                logger.error(f"Error transcribing {audio_path}: {e}")
                transcripts.append("")
        
        return transcripts
