import requests

def collect(username):
    """Check if a public LinkedIn profile exists"""
    signals = []
    try:
        url = f"https://www.linkedin.com/in/{username}"
        r = requests.head(url, timeout=10)
        if r.status_code == 200:
            signals.append({"signal_type": "PROFILE_PLATFORM", "value": "Public LinkedIn profile detected", "confidence": "HIGH"})
        else:
            signals.append({"signal_type": "PROFILE_PLATFORM", "value": "No public LinkedIn profile detected", "confidence": "LOW"})
    except Exception as e:
        signals.append({"signal_type": "PROFILE_PLATFORM", "value": f"Error checking LinkedIn: {e}", "confidence": "LOW"})
    return signals
