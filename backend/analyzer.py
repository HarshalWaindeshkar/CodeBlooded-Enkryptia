import json
import re
import os

# Load keywords file
KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'hype_keywords.json')

with open(KEYWORDS_PATH, 'r') as f:
    keywords_data = json.load(f)

HYPE_KEYWORDS = [kw.lower() for kw in keywords_data['hype_keywords']]
DISCLAIMER_PHRASES = [dp.lower() for dp in keywords_data['disclaimer_phrases']]


def detect_hype_keywords(text: str) -> dict:
    """
    Scans transcript for hype/risky keywords.
    Returns list of found keywords and their count.
    """
    text_lower = text.lower()
    found = []

    for keyword in HYPE_KEYWORDS:
        if keyword in text_lower:
            # Count how many times it appears
            count = text_lower.count(keyword)
            found.append({"keyword": keyword, "count": count})

    return {
        "found_keywords": found,
        "total_matches": sum(item["count"] for item in found),
        "unique_matches": len(found)
    }


def detect_disclaimers(text: str) -> dict:
    """
    Checks whether the video includes standard financial disclaimers.
    """
    text_lower = text.lower()
    found_disclaimers = []

    for phrase in DISCLAIMER_PHRASES:
        if phrase in text_lower:
            found_disclaimers.append(phrase)

    has_disclaimer = len(found_disclaimers) > 0

    return {
        "has_disclaimer": has_disclaimer,
        "found_disclaimers": found_disclaimers,
        "missing_disclaimer": not has_disclaimer
    }


def detect_exaggerated_claims(text: str) -> dict:
    """
    Uses regex to find exaggerated numerical claims.
    e.g. '500%', '1000x', '$10,000 in one week'
    """
    patterns = [
    r'\d+x\s*(return|profit|gain|your money)?',   # 10x, 100x
    r'\d+\s*%\s*(profit|return|gain|interest)',    # 500% profit
    r'\$[\d,]+\s*in\s*(one|a)\s*\w+',             # $10,000 in one week
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
            found_patterns.append({
                "pattern": pattern,
                "matches": len(matches)
            })

    return {
        "exaggerated_claims": found_patterns,
        "total_exaggerations": len(found_patterns)
    }


def analyze_transcript(text: str) -> dict:
    """
    Master function — runs all analysis and returns combined results.
    """
    hype = detect_hype_keywords(text)
    disclaimers = detect_disclaimers(text)
    exaggerations = detect_exaggerated_claims(text)

    return {
        "hype_analysis": hype,
        "disclaimer_analysis": disclaimers,
        "exaggeration_analysis": exaggerations,
        "transcript_length": len(text.split()),
    }