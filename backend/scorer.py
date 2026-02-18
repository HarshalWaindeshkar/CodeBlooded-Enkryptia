def calculate_risk_score(analysis: dict) -> dict:
    """
    Converts NLP analysis into a 0-10 risk score.
    Higher = more risky/misleading content.
    """
    score = 0
    reasons = []

    hype = analysis["hype_analysis"]
    disclaimer = analysis["disclaimer_analysis"]
    exaggeration = analysis["exaggeration_analysis"]

    # Rule 1: Hype keywords (max 4 points)
    unique_hype = hype["unique_matches"]
    if unique_hype >= 6:
        score += 4
        reasons.append(f"🚨 {unique_hype} hype keywords detected")
    elif unique_hype >= 3:
        score += 2.5
        reasons.append(f"⚠️ {unique_hype} hype keywords detected")
    elif unique_hype >= 1:
        score += 1
        reasons.append(f"📌 {unique_hype} hype keyword(s) detected")

    # Rule 2: Missing disclaimer (max 3 points)
    if disclaimer["missing_disclaimer"]:
        score += 3
        reasons.append("🚨 No financial disclaimer found")
    else:
        reasons.append("✅ Disclaimer present")

    # Rule 3: Exaggerated claims (max 3 points)
    exag_count = exaggeration["total_exaggerations"]
    if exag_count >= 3:
        score += 3
        reasons.append(f"🚨 {exag_count} exaggerated claims detected")
    elif exag_count >= 1:
        score += 1.5
        reasons.append(f"⚠️ {exag_count} exaggerated claim(s) detected")

    # Cap at 10
    score = min(round(score, 1), 10)

    # Risk label
    if score >= 7:
        label = "🔴 HIGH RISK"
    elif score >= 4:
        label = "🟡 MEDIUM RISK"
    else:
        label = "🟢 LOW RISK"

    return {
        "risk_score": score,
        "risk_label": label,
        "reasons": reasons
    }