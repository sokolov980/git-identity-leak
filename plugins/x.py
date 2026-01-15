# git_identity_leak/plugins/x.py
import requests
from datetime import datetime

BASE_URL = "https://nitter.net"  # Use nitter for scraping X without API

def collect(username: str):
    signals = []

    try:
        url = f"{BASE_URL}/{username}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            # Signal: profile exists
            signals.append({
                "value": username,
                "confidence": 0.8,
                "signal_type": "FACT",
                "evidence": f"X profile found at {url}",
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat()
            })

            # Extract profile avatar URL (very basic)
            import re
            match = re.search(r'<img class="profile-card-avatar" src="([^"]+)"', resp.text)
            if match:
                avatar_url = match.group(1)
                if avatar_url.startswith("//"):
                    avatar_url = "https:" + avatar_url
                signals.append({
                    "value": avatar_url,
                    "confidence": 0.9,
                    "signal_type": "IMAGE",
                    "evidence": f"X profile avatar",
                    "first_seen": datetime.utcnow().isoformat(),
                    "last_seen": datetime.utcnow().isoformat()
                })
    except Exception as e:
        print(f"[!] X plugin error for {username}: {e}")

    return signals
