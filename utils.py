def normalize_confidence(value, platform_weight=1.0):
    """
    Normalize confidence to 0-1 scale and weight by platform.
    """
    value = max(0.0, min(1.0, value))
    return value * platform_weight

def decay_over_time(confidence, days):
    """
    Reduce confidence over time (older signals are less reliable).
    """
    decay_rate = 0.01
    return max(0.0, confidence - decay_rate * days)
