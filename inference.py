from schemas import Signal

def apply_inference(signals: list[Signal]) -> list[Signal]:
    """
    Classify signals as FACT or INFERENCE based on source and confidence.
    """
    for s in signals:
        if s.confidence >= 0.75:
            s.signal_type = "FACT"
        else:
            s.signal_type = "INFERENCE"
    return signals
