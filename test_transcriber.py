from backend.utils import download_audio
from backend.transcriber import transcribe_audio
from backend.analyzer import analyze_transcript
from backend.scorer import calculate_risk_score

TEST_URL = "https://www.youtube.com/watch?v=2T0OUIW89II"

print("Step 1: Downloading audio...")
audio_path, title, duration = download_audio(TEST_URL)
print(f"Downloaded: {title}")

print("\nStep 2: Transcribing...")
transcript = transcribe_audio(audio_path)
print(f"Language: {transcript['language']}")
print(f"Words: {len(transcript['text'].split())}")

print("\nStep 3: Analyzing...")
analysis = analyze_transcript(transcript['text'])
print(f"Hype keywords found: {analysis['hype_analysis']['unique_matches']}")
print(f"Disclaimer present: {analysis['disclaimer_analysis']['has_disclaimer']}")

print("\nStep 4: Risk Score...")
result = calculate_risk_score(analysis)
print(f"Risk Score: {result['risk_score']}/10")
print(f"Risk Label: {result['risk_label']}")
print("Reasons:")
for r in result['reasons']:
    print(f"  {r}")