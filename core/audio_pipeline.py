import os
import numpy as np
import soundfile as sf
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioPipeline:
    """Robust and fast audio processing pipeline for GenAI transcription."""

    def __init__(self, sample_rate=16000, chunk_duration=30):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_samples = sample_rate * chunk_duration
        self.temp_dir = tempfile.gettempdir()

    # =========================================================
    # 🔧 UNIVERSAL AUDIO CONVERTER (m4a, webm, mp3 → wav)
    # =========================================================
    def _convert_to_wav(self, input_path):
        """Convert any audio format to WAV using FFmpeg."""
        import subprocess
        import shutil

        input_path = os.path.abspath(input_path)
        wav_path = os.path.splitext(input_path)[0] + ".wav"

        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg and add it to PATH."
            )

        logger.info(f"Converting audio to WAV: {input_path}")

        cmd = [
            ffmpeg_path,
            "-y",
            "-i", input_path,
            "-ac", "1",
            "-ar", str(self.sample_rate),
            "-acodec", "pcm_s16le",
            wav_path
        ]

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        if not os.path.exists(wav_path):
            raise RuntimeError("Audio conversion to WAV failed")

        return wav_path

    # =========================================================
    # 🎧 AUDIO LOADER
    # =========================================================
    def load_audio(self, audio_path):
        """Load audio file safely (YouTube/Windows/FFmpeg safe)."""
        import shutil
        import subprocess
        import tempfile
        from pathlib import Path

        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(audio_path)

            # --- 1. COPY TO SAFE TEMP FILE ---
            ext = Path(audio_path).suffix.lower()
            safe_input = os.path.join(tempfile.gettempdir(), f"audio_input{ext}")
            shutil.copy2(audio_path, safe_input)

            # --- 2. CONVERT TO WAV USING SAFE FFmpeg FLAGS ---
            safe_wav = os.path.join(tempfile.gettempdir(), "audio_converted.wav")

            ffmpeg = shutil.which("ffmpeg")
            if not ffmpeg:
                raise RuntimeError("FFmpeg not found in PATH")

            cmd = [
                ffmpeg,
                "-y",
                "-loglevel", "error",
                "-probesize", "50M",
                "-analyzeduration", "50M",
                "-i", safe_input,
                "-vn",
                "-map", "a:0",
                "-ac", "1",
                "-ar", str(self.sample_rate),
                "-c:a", "pcm_s16le",
                "-f", "wav",
                safe_wav
            ]

            subprocess.run(cmd, capture_output=True, check=True)

            # --- 3. LOAD WAV ---
            audio, sr = sf.read(safe_wav, dtype=np.float32)

            # Resample if needed
            if sr != self.sample_rate:
                from scipy.signal import resample
                audio = resample(audio, int(len(audio) * self.sample_rate / sr))

            # Mono
            if audio.ndim > 1:
                audio = audio.mean(axis=1)

            # Normalize
            audio /= max(abs(audio).max(), 1e-6)

            return audio.astype(np.float32)

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed: {e.stderr.decode(errors='ignore')}")
            raise
        except Exception as e:
            logger.error(f"Audio loading failed: {e}")
            raise

    # =========================================================
    # ✂️ AUDIO CHUNKING
    # =========================================================
    def chunk_audio(self, audio, overlap=5):
        """Split audio into overlapping chunks."""
        chunks = []
        step = self.chunk_samples - int(self.sample_rate * overlap)

        start = 0
        while start < len(audio):
            end = min(start + self.chunk_samples, len(audio))
            chunks.append(audio[start:end])
            start += step

        return chunks

    # =========================================================
    # 💾 SAVE CHUNKS
    # =========================================================
    def save_chunk(self, chunk, index):
        chunk_path = os.path.join(self.temp_dir, f"chunk_{index}.wav")
        sf.write(chunk_path, chunk, self.sample_rate)
        return chunk_path

    # =========================================================
    # 🎤 SIMPLE VAD (Silence Removal)
    # =========================================================
    def apply_vad(self, audio, threshold=0.02):
        """Energy-based Voice Activity Detection."""
        frame_len = int(0.025 * self.sample_rate)
        hop = frame_len // 2

        energies = []
        for i in range(0, len(audio) - frame_len, hop):
            frame = audio[i:i + frame_len]
            energies.append(np.sqrt(np.mean(frame ** 2)))

        energies = np.array(energies)
        mask = energies > (np.mean(energies) * threshold)

        full_mask = np.zeros(len(audio), dtype=bool)
        for i, active in enumerate(mask):
            start = i * hop
            end = min(start + frame_len, len(audio))
            full_mask[start:end] = active

        return audio[full_mask]

    # =========================================================
    # 🔄 NORMALIZATION
    # =========================================================
    def normalize_audio(self, audio):
        max_val = np.abs(audio).max()
        if max_val > 0:
            return audio / max_val
        return audio

    # =========================================================
    # 🚀 FULL PIPELINE
    # =========================================================
    def process_audio_file(self, audio_path, apply_vad=True):
        audio = self.load_audio(audio_path)

        if apply_vad:
            audio = self.apply_vad(audio)

        audio = self.normalize_audio(audio)
        return audio

    # =========================================================
    # 🧠 PREPARE FOR TRANSCRIPTION
    # =========================================================
    def get_audio_chunks_for_processing(self, audio_path, apply_vad=True):
        audio = self.process_audio_file(audio_path, apply_vad=apply_vad)
        chunks = self.chunk_audio(audio)

        chunk_paths = []
        for i, chunk in enumerate(chunks):
            path = self.save_chunk(chunk, i)
            chunk_paths.append(path)

        return chunk_paths, audio

    # =========================================================
    # 🧹 CLEANUP
    # =========================================================
    def cleanup_chunks(self, chunk_paths):
        for path in chunk_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                logger.warning(f"Could not delete chunk {path}: {e}")
