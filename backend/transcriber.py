import whisper
import os

# Load model once at module level (saves time on repeated calls)
# Options: "tiny", "base", "small", "medium", "large"
# For hackathon: "base" is the sweet spot — fast + accurate enough
model = whisper.load_model("base")

def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribes an audio file using Whisper.
    Returns transcript text and detected language.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"Transcribing: {audio_path}")
    result = model.transcribe(audio_path, fp16=False)

    return {
        "text": result["text"].strip(),
        "language": result.get("language", "unknown"),
        "segments": result.get("segments", [])
    }