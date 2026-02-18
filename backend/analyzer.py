import json
import re
import os
from transformers import pipeline

print("Loading FinBERT model...")
finbert = pipeline(
    "text-classification",
    model="ProsusAI/finbert",
    truncation=True,
    max_length=512
)
print("FinBERT loaded!")

KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'hype_keywords.json')
with open(KEYWORDS_PATH, 'r') as f:
    keywords_data = json.load(f)

HYPE_KEYWORDS = [kw.lower() for kw in keywords_data['hype_keywords']]
DISCLAIMER_PHRASES = [dp.lower() for dp in keywords_data['disclaimer_phrases']]


def detect_hype_keywords(text: str) -> dict:
    text_lower = text.lower()
    found = []
    for keyword in HYPE_KEYWORDS:
        if keyword in text_lower:
            count = text_lower.count(keyword)
            found.append({"keyword": keyword, "count": count})
    return {
        "found_keywords": found,
        "total_matches": sum(item["count"] for item in found),
        "unique_matches": len(found)
    }


def detect_disclaimers(text: str) -> dict:
    text_lower = text.lower()
    found_disclaimers = []
    for phrase in DISCLAIMER_PHRASES:
        if phrase in text_lower:
            found_disclaimers.append(phrase)
    return {
        "has_disclaimer": len(found_disclaimers) > 0,
        "found_disclaimers": found_disclaimers,
        "missing_disclaimer": len(found_disclaimers) == 0
    }


def detect_exaggerated_claims(text: str) -> dict:
    patterns = [
        r'\d+x\s*(return|profit|gain|your money)?',
        r'\d+\s*%\s*(profit|return|gain|interest)',
        r'\$[\d,]+\s*in\s*(one|a)\s*\w+',
        r'(double|triple|quadruple)\s*(your)?\s*money',
        r'(never|always)\s*(lose|fail)',
        r'(guaranteed|promise|assure)\s*(you|returns|profit|gains)?',
        r'(quit|leave)\s*(your)?\s*(job|work|9\s*to\s*5)',
        r'(retire|retirement)\s*(early|at \d+|by \d+)',
        r'made?\s*\$[\d,]+\s*in\s*(a day|one day|a week|one week|a month)',
    ]
    found_patterns = []
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            found_patterns.append({"pattern": pattern, "matches": len(matches)})
    return {
        "exaggerated_claims": found_patterns,
        "total_exaggerations": len(found_patterns)
    }


def analyze_with_finbert(text: str) -> dict:
    words = text.split()
    chunk_size = 300
    chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

    results = []
    for chunk in chunks[:5]:
        if len(chunk.strip()) > 20:
            result = finbert(chunk)[0]
            results.append(result)

    if not results:
        return {"sentiment": "neutral", "confidence": 0.0, "positive_ratio": 0.0,
                "positive_chunks": 0, "negative_chunks": 0, "neutral_chunks": 0, "total_chunks": 0}

    positive = sum(1 for r in results if r['label'] == 'positive')
    negative = sum(1 for r in results if r['label'] == 'negative')
    neutral = sum(1 for r in results if r['label'] == 'neutral')
    total = len(results)

    positive_ratio = positive / total
    avg_confidence = sum(r['score'] for r in results) / total

    dominant = max(
        [('positive', positive), ('negative', negative), ('neutral', neutral)],
        key=lambda x: x[1]
    )[0]

    return {
        "sentiment": dominant,
        "confidence": round(avg_confidence, 3),
        "positive_ratio": round(positive_ratio, 3),
        "positive_chunks": positive,
        "negative_chunks": negative,
        "neutral_chunks": neutral,
        "total_chunks": total
    }


def analyze_transcript(text: str) -> dict:
    hype = detect_hype_keywords(text)
    disclaimers = detect_disclaimers(text)
    exaggerations = detect_exaggerated_claims(text)
    finbert_result = analyze_with_finbert(text)

    return {
        "hype_analysis": hype,
        "disclaimer_analysis": disclaimers,
        "exaggeration_analysis": exaggerations,
        "finbert_analysis": finbert_result,
        "transcript_length": len(text.split()),
    }