# plugins/x.py

import requests

def collect(username):
    """
    Fetch public X posts by username (if possible without auth)
    """
    signals = []
    try:
        url = f"https://nitter.net/{username}"  # Nitter provides a public Twitter frontend without API
        resp = requests.get(url)
        if resp.status_code == 200:
            signals.append({"signal_type": "POST_PLATFORM", "value": "X/Nitter public posts found", "confidence": "MEDIUM", "source": "X"})
        else:
            signals.append({"signal_type": "POST_PLATFORM", "value": "No public X posts detected", "confidence": "LOW", "source": "X"})
    except Exception as e:
        print(f"[!] Error collecting X posts: {e}")
    return signals
