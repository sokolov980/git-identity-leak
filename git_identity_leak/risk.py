def summarize_risk(signals):
    """
    Produce a simple risk summary based on collected signals.
    """

    drivers = []
    score = 0.0

    for s in signals:
        stype = s.get("signal_type")
        val = s.get("value")

        if stype == "USERNAME":
            drivers.append({
                "driver": f"Username reuse: {val}",
                "score": 0.9
            })
            score += 0.9

        elif stype == "EMAIL":
            drivers.append({
                "driver": f"Email exposure: {val}",
                "score": 0.8
            })
            score += 0.8

        elif stype == "IMAGE":
            drivers.append({
                "driver": "Public profile image",
                "score": 0.6
            })
            score += 0.6

        elif stype == "POST_PLATFORM":
            drivers.append({
                "driver": "Public posts linked to identity",
                "score": 0.5
            })
            score += 0.5

    overall_risk = "LOW"
    if score >= 1.5:
        overall_risk = "MEDIUM"
    if score >= 3.0:
        overall_risk = "HIGH"

    return {
        "overall_risk": overall_risk,
        "drivers": drivers
    }
