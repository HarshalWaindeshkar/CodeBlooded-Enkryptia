import whisper
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

model = whisper.load_model("base")

def transcribe_audio(audio_path: str) -> dict:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"Transcribing: {audio_path}")
    result = model.transcribe(audio_path, fp16=False)

    return {
        "text": result["text"].strip(),
        "language": result.get("language", "unknown"),
        "segments": result.get("segments", [])
    }