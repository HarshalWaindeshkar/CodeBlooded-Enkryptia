import json
import re
import os
import logging
from functools import lru_cache
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

KEYWORDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'hype_keywords.json')

def _load_keywords() -> tuple:
    try:
        with open(KEYWORDS_PATH, 'r') as f:
            data = json.load(f)
        if 'hype_keywords' not in data or 'disclaimer_phrases' not in data:
            raise ValueError("hype_keywords.json must contain 'hype_keywords' and 'disclaimer_phrases' keys.")
        return (
            [kw.lower() for kw in data['hype_keywords']],
            [dp.lower() for dp in data['disclaimer_phrases']]
        )
    except FileNotFoundError:
        logger.error(f"Keywords file not found at: {KEYWORDS_PATH}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in keywords file: {e}")
        raise

HYPE_KEYWORDS, DISCLAIMER_PHRASES = _load_keywords()

# ── Lazy FinBERT loader ───────────────────────────────────────────────────────

_finbert = None

def get_finbert():
    global _finbert
    if _finbert is None:
        try:
            from transformers import pipeline
            logger.info("Loading FinBERT model...")
            _finbert = pipeline(
                "text-classification",
                model="ProsusAI/finbert",
                truncation=True,
                max_length=512
            )
            logger.info("FinBERT loaded!")
        except Exception as e:
            logger.error(f"Failed to load FinBERT: {e}")
            raise
    return _finbert

# ── Analysis functions ────────────────────────────────────────────────────────

def detect_hype_keywords(text: str) -> dict:
    if not text or not text.strip():
        return {"found_keywords": [], "total_matches": 0, "unique_matches": 0, "severity": "low"}

    text_lower = text.lower()
    found = []
    for keyword in HYPE_KEYWORDS:
        count = text_lower.count(keyword)
        if count > 0:
            found.append({"keyword": keyword, "count": count})

    total = sum(item["count"] for item in found)
    unique = len(found)
    severity = "low" if total < 3 else ("medium" if total <= 7 else "high")

    return {
        "found_keywords": found,
        "total_matches": total,
        "unique_matches": unique,
        "severity": severity
    }


def detect_disclaimers(text: str) -> dict:
    if not text or not text.strip():
        return {"has_disclaimer": False, "found_disclaimers": [], "missing_disclaimer": True}

    text_lower = text.lower()
    found_disclaimers = [phrase for phrase in DISCLAIMER_PHRASES if phrase in text_lower]

    return {
        "has_disclaimer": len(found_disclaimers) > 0,
        "found_disclaimers": found_disclaimers,
        "missing_disclaimer": len(found_disclaimers) == 0
    }


def detect_exaggerated_claims(text: str) -> dict:
    if not text or not text.strip():
        return {"exaggerated_claims": [], "total_exaggerations": 0, "severity": "low"}

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
        r'(passive\s*income|financial\s*freedom|wealth\s*building)',
        r'(no\s*risk|risk[\s-]free|zero\s*risk)',
        r'(secret|they\s*don\'t\s*want\s*you\s*to\s*know)',
        r'(once[\s-]in[\s-]a[\s-]lifetime|limited\s*time\s*offer)',
    ]

    found_patterns = []
    text_lower = text.lower()
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            found_patterns.append({"pattern": pattern, "matches": len(matches)})

    total = len(found_patterns)
    severity = "low" if total < 2 else ("medium" if total <= 4 else "high")

    return {
        "exaggerated_claims": found_patterns,
        "total_exaggerations": total,
        "severity": severity
    }


def _chunk_text_with_overlap(text: str, chunk_size: int = 300, overlap: int = 50) -> list:
    """Split text into overlapping word chunks to avoid cutting sentences mid-thought."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        if len(chunk.strip()) > 20:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


@lru_cache(maxsize=128)
def _cached_finbert(text_chunk: str) -> dict:
    """Cache FinBERT results for repeated chunks."""
    finbert = get_finbert()
    return finbert(text_chunk)[0]


def analyze_with_finbert(text: str) -> dict:
    if not text or not text.strip():
        return {"sentiment": "neutral", "confidence": 0.0, "positive_ratio": 0.0,
                "positive_chunks": 0, "negative_chunks": 0, "neutral_chunks": 0, "total_chunks": 0}

    try:
        chunks = _chunk_text_with_overlap(text)[:5]
        results = []
        for chunk in chunks:
            result = _cached_finbert(chunk)
            results.append(result)

        if not results:
            return {"sentiment": "neutral", "confidence": 0.0, "positive_ratio": 0.0,
                    "positive_chunks": 0, "negative_chunks": 0, "neutral_chunks": 0, "total_chunks": 0}

        positive = sum(1 for r in results if r['label'] == 'positive')
        negative = sum(1 for r in results if r['label'] == 'negative')
        neutral  = sum(1 for r in results if r['label'] == 'neutral')
        total    = len(results)

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

    except Exception as e:
        logger.error(f"FinBERT analysis failed: {e}")
        return {"sentiment": "unknown", "confidence": 0.0, "positive_ratio": 0.0,
                "positive_chunks": 0, "negative_chunks": 0, "neutral_chunks": 0,
                "total_chunks": 0, "error": str(e)}


# ── Overall Hype/Risk Score ───────────────────────────────────────────────────

def compute_hype_score(hype: dict, disclaimers: dict, exaggerations: dict, finbert_result: dict) -> dict:
    """
    Produce a 0-100 hype/risk score from all signals.

    Weights:
      - Hype keywords      : 25 pts
      - No disclaimer      : 20 pts
      - Exaggerated claims : 30 pts
      - FinBERT positive   : 25 pts
    """
    score = 0

    # Hype keywords (0-25)
    kw_total = hype.get("total_matches", 0)
    kw_score = min(kw_total * 2.5, 25)
    score += kw_score

    # Missing disclaimer (0-20)
    if disclaimers.get("missing_disclaimer", True):
        score += 20

    # Exaggerated claims (0-30)
    exag_total = exaggerations.get("total_exaggerations", 0)
    exag_score = min(exag_total * 6, 30)
    score += exag_score

    # FinBERT positive sentiment (0-25)
    positive_ratio = finbert_result.get("positive_ratio", 0.0)
    finbert_score = round(positive_ratio * 25, 2)
    score += finbert_score

    score = round(min(score, 100), 2)

    if score < 30:
        risk_level = "Low"
    elif score < 60:
        risk_level = "Medium"
    elif score < 80:
        risk_level = "High"
    else:
        risk_level = "Very High"

    return {
        "hype_score": score,
        "risk_level": risk_level,
        "score_breakdown": {
            "hype_keywords_contribution": round(kw_score, 2),
            "missing_disclaimer_contribution": 20 if disclaimers.get("missing_disclaimer") else 0,
            "exaggeration_contribution": round(exag_score, 2),
            "finbert_positive_contribution": finbert_score
        }
    }


# ── Main entry point ──────────────────────────────────────────────────────────

def analyze_transcript(text: str) -> dict:
    if not text or not text.strip():
        logger.warning("Empty text passed to analyze_transcript.")
        return {"error": "Input text is empty or None."}

    try:
        hype          = detect_hype_keywords(text)
        disclaimers   = detect_disclaimers(text)
        exaggerations = detect_exaggerated_claims(text)
        finbert_result = analyze_with_finbert(text)
        hype_score    = compute_hype_score(hype, disclaimers, exaggerations, finbert_result)

        return {
            "hype_score": hype_score,
            "hype_analysis": hype,
            "disclaimer_analysis": disclaimers,
            "exaggeration_analysis": exaggerations,
            "finbert_analysis": finbert_result,
            "transcript_length": len(text.split()),
        }

    except Exception as e:
        logger.error(f"analyze_transcript failed: {e}")
        return {"error": str(e)}