import requests


def collect(username):
    url = f"https://www.linkedin.com/in/{username}"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return [{
                "signal_type": "PROFILE_PLATFORM",
                "value": "Public LinkedIn profile detected",
                "confidence": "MEDIUM"
            }]
    except Exception:
        pass

    return [{
        "signal_type": "PROFILE_PLATFORM",
        "value": "No public LinkedIn profile detected",
        "confidence": "LOW"
    }]
