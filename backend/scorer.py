def calculate_risk_score(analysis: dict) -> dict:
    score = 0
    reasons = []

    hype = analysis["hype_analysis"]
    disclaimer = analysis["disclaimer_analysis"]
    exaggeration = analysis["exaggeration_analysis"]
    finbert = analysis["finbert_analysis"]

    # Rule 1: Hype keywords (max 3 points)
    unique_hype = hype["unique_matches"]
    if unique_hype >= 6:
        score += 3
        reasons.append(f"🚨 {unique_hype} hype keywords detected")
    elif unique_hype >= 3:
        score += 2
        reasons.append(f"⚠️ {unique_hype} hype keywords detected")
    elif unique_hype >= 1:
        score += 1
        reasons.append(f"📌 {unique_hype} hype keyword(s) detected")

    # Rule 2: Missing disclaimer (2 points)
    if disclaimer["missing_disclaimer"]:
        score += 2
        reasons.append("🚨 No financial disclaimer found")
    else:
        reasons.append("✅ Disclaimer present")

    # Rule 3: Exaggerated claims (max 2 points)
    exag_count = exaggeration["total_exaggerations"]
    if exag_count >= 3:
        score += 2
        reasons.append(f"🚨 {exag_count} exaggerated claims detected")
    elif exag_count >= 1:
        score += 1
        reasons.append(f"⚠️ {exag_count} exaggerated claim(s) detected")

    # Rule 4: FinBERT sentiment (max 3 points)
    positive_ratio = finbert["positive_ratio"]
    sentiment = finbert["sentiment"]
    confidence = finbert["confidence"]

    if positive_ratio >= 0.7:
        score += 3
        reasons.append(f"🚨 FinBERT: Overwhelmingly positive sentiment ({int(positive_ratio*100)}%) — potential hype")
    elif positive_ratio >= 0.5:
        score += 2
        reasons.append(f"⚠️ FinBERT: High positive sentiment ({int(positive_ratio*100)}%) — overconfident tone")
    elif positive_ratio >= 0.3:
        score += 1
        reasons.append(f"📌 FinBERT: Moderately positive sentiment ({int(positive_ratio*100)}%)")
    else:
        reasons.append(f"✅ FinBERT: Balanced sentiment ({sentiment}, {int(confidence*100)}% confidence)")

    score = min(round(score, 1), 10)

    if score >= 7:
        label = "🔴 HIGH RISK"
    elif score >= 4:
        label = "🟡 MEDIUM RISK"
    else:
        label = "🟢 LOW RISK"

    return {
        "risk_score": score,
        "risk_label": label,
        "reasons": reasons,
        "finbert_sentiment": finbert["sentiment"],
        "finbert_confidence": finbert["confidence"]
    }