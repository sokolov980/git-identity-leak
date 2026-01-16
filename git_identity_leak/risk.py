def compute_risk(signals: list, graph) -> dict:
    """
    Compute overall risk score and per-driver breakdown.
    """
    overall_risk = 0.0
    drivers = []

    for s in signals:
        weight = s.confidence
        if s.type == "username" and s.signal_type == "FACT":
            drivers.append({"driver": f"Username reuse: {s.value}", "score": weight})
            overall_risk += 0.3 * weight
        elif s.type == "email" and s.signal_type == "FACT":
            drivers.append({"driver": f"Email exposure: {s.value}", "score": weight})
            overall_risk += 0.25 * weight
        elif s.type == "image" and s.signal_type == "INFERENCE":
            drivers.append({"driver": f"Image link: {s.value}", "score": weight})
            overall_risk += 0.15 * weight
        elif s.type == "post":
            drivers.append({"driver": f"Post content: {s.value[:30]}...", "score": weight})
            overall_risk += 0.1 * weight

    overall_risk = min(overall_risk, 1.0)
    return {"overall_risk": "HIGH" if overall_risk > 0.6 else "MEDIUM" if overall_risk > 0.3 else "LOW",
            "drivers": drivers}
