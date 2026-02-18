from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import traceback

from backend.utils import download_audio
from backend.transcriber import transcribe_audio
from backend.analyzer import analyze_transcript
from backend.scorer import calculate_risk_score

app = FastAPI(
    title="AI Finfluencer Risk Detector",
    description="Analyzes financial videos for misleading or risky content",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.get("/")
def root():
    return {"message": "Finfluencer Risk Detector API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/analyze")
def analyze_video(request: VideoRequest):
    if "youtube.com" not in request.url and "youtu.be" not in request.url:
        raise HTTPException(status_code=400, detail="Only YouTube URLs are supported")

    audio_path = None

    try:
        print(f"Downloading: {request.url}")
        audio_path, title, duration = download_audio(request.url)
        print(f"Downloaded: {title}")

        print("Transcribing...")
        transcript = transcribe_audio(audio_path)
        print(f"Words: {len(transcript['text'].split())}")

        print("Analyzing...")
        analysis = analyze_transcript(transcript["text"])

        print("Scoring...")
        score = calculate_risk_score(analysis)
        print(f"Score: {score['risk_score']}/10")

        return {
            "success": True,
            "video_title": title,
            "duration_seconds": duration,
            "language": transcript["language"],
            "transcript_preview": transcript["text"][:300],
            "full_transcript": transcript["text"],        # ← added
            "risk_score": score["risk_score"],
            "risk_label": score["risk_label"],
            "reasons": score["reasons"],
            "hype_keywords_found": analysis["hype_analysis"]["found_keywords"],
            "disclaimer_found": analysis["disclaimer_analysis"]["has_disclaimer"],
            "found_disclaimers": analysis["disclaimer_analysis"]["found_disclaimers"],
            "word_count": analysis["transcript_length"],
            "finbert_sentiment": score.get("finbert_sentiment", "neutral"),
            "finbert_confidence": score.get("finbert_confidence", 0.0)
        }

    except Exception as e:
        print("ERROR:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            print("Temp audio deleted")