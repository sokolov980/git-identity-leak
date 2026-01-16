# git_identity_leak/plugins/reddit.py
import requests
from datetime import datetime

def collect(username):
    collected_at = datetime.utcnow().isoformat() + "Z"
    url = f"https://www.reddit.com/user/{username}.json"
    headers = {"User-Agent": "git-identity-leak"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200 and r.json().get("data"):
            return [{
                "signal_type": "POST_PLATFORM",
                "value": "Reddit activity detected",
                "confidence": "MEDIUM",
                "source": "Reddit",
                "collected_at": collected_at
            }]
    except Exception:
        pass

    return [{
        "signal_type": "POST_PLATFORM",
        "value": "No Reddit posts detected",
        "confidence": "LOW",
        "source": "Reddit",
        "collected_at": collected_at
    }]
