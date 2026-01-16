# git_identity_leak/plugins/x.py
import requests
from datetime import datetime

def collect(username):
    collected_at = datetime.utcnow().isoformat() + "Z"
    # Use Nitter to avoid X API/SSL issues
    url = f"https://nitter.net/{username}"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return [{
                "signal_type": "PROFILE_PLATFORM",
                "value": "Public X profile detected",
                "confidence": "MEDIUM",
                "source": "X",
                "collected_at": collected_at
            }]
    except Exception:
        pass

    return [{
        "signal_type": "PROFILE_PLATFORM",
        "value": "No public X profile detected",
        "confidence": "LOW",
        "source": "X",
        "collected_at": collected_at
    }]
