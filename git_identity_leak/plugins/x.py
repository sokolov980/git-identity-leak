import requests


def collect(username):
    url = f"https://twitter.com/{username}"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return [{
                "signal_type": "PROFILE_PLATFORM",
                "value": "Public X profile detected",
                "confidence": "MEDIUM"
            }]
    except Exception:
        pass

    return [{
        "signal_type": "PROFILE_PLATFORM",
        "value": "No public X profile detected",
        "confidence": "LOW"
    }]
