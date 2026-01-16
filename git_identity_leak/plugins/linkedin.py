# git_identity_leak/plugins/linkedin.py
import requests
from datetime import datetime

def collect(username):
    collected_at = datetime.utcnow().isoformat() + "Z"
    url = f"https://www.linkedin.com/in/{username}"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return [{
                "signal_type": "PROFILE_PLATFORM",
                "value": "Public LinkedIn profile detected",
                "confidence": "MEDIUM",
                "source": "LinkedIn",
                "collected_at": collected_at
            }]
    except Exception:
        pass

    return [{
        "signal_type": "PROFILE_PLATFORM",
        "value": "No public LinkedIn profile detected",
        "confidence": "LOW",
        "source": "LinkedIn",
        "collected_at": collected_at
    }]
