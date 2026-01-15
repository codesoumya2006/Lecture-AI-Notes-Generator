from services.whisper_loader import load_whisper_model

def transcribe_audio(audio_path: str) -> str:
    model = load_whisper_model()
    result = model.transcribe(audio_path)
    return result["text"]
