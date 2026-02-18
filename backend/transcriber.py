import whisper
import os
import ssl
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SSL fix
ssl._create_default_https_context = ssl._create_unverified_context

# ── Lazy model loader ─────────────────────────────────────────────────────────

_model = None

def get_model():
    global _model
    if _model is None:
        logger.info("Loading Whisper model...")
        _model = whisper.load_model("base")
        logger.info("Whisper model loaded!")
    return _model


# ── Audio validation ──────────────────────────────────────────────────────────

def validate_audio(audio_path: str) -> None:
    """Validate audio before passing to Whisper to prevent tensor reshape crashes."""

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    file_size = os.path.getsize(audio_path)
    if file_size < 1000:
        raise ValueError(
            f"Audio file too small ({file_size} bytes) — "
            f"likely a failed download or corrupt FFmpeg output: {audio_path}"
        )

    # Use whisper's own audio loader to validate (no extra dependencies)
    try:
        audio = whisper.load_audio(audio_path)
        duration = len(audio) / whisper.audio.SAMPLE_RATE

        if duration < 0.5:
            raise ValueError(
                f"Audio too short ({duration:.2f}s). Whisper needs at least 0.5s."
            )

        if np.max(np.abs(audio)) < 1e-4:
            raise ValueError(
                f"Audio appears silent (max amplitude: {np.max(np.abs(audio)):.6f})."
            )

        logger.info(f"Audio validated — Duration: {duration:.2f}s | Size: {file_size} bytes")

    except (ValueError, FileNotFoundError):
        raise
    except Exception as e:
        raise RuntimeError(f"Could not read audio file '{audio_path}': {e}") from e


# ── Transcription ─────────────────────────────────────────────────────────────

def transcribe_audio(audio_path: str) -> dict:
    validate_audio(audio_path)

    model = get_model()

    try:
        logger.info(f"Transcribing: {audio_path}")

        # Detect language first to avoid empty segment tensor issues
        audio = whisper.load_audio(audio_path)
        audio_trimmed = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio_trimmed).to(model.device)

        _, probs = model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)
        logger.info(f"Detected language: {detected_lang} (confidence: {probs[detected_lang]:.2f})")

        # Explicit language prevents reshape errors on ambiguous/short segments
        result = model.transcribe(
            audio_path,
            fp16=False,
            language=detected_lang,
            condition_on_previous_text=False,
            verbose=False
        )

        text = result["text"].strip()

        if not text:
            logger.warning("Whisper returned empty transcription.")
            return {
                "text": "",
                "language": detected_lang,
                "segments": [],
                "warning": "Transcription returned empty. Audio may be unclear."
            }

        logger.info(f"Transcription complete — {len(text.split())} words | lang: {detected_lang}")

        return {
            "text": text,
            "language": detected_lang,
            "segments": result.get("segments", [])
        }

    except RuntimeError as e:
        err = str(e)
        if "reshape" in err or "tensor" in err or "shape" in err:
            logger.error(f"Whisper tensor error — empty or corrupt audio segment: {e}")
            raise RuntimeError(
                "Whisper failed to process the audio. "
                "The clip may be too short, silent, or in an unsupported format. "
                f"Details: {e}"
            ) from e
        raise

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise