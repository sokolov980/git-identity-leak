# git_identity_leak/plugins/linkedin.py
import requests
from datetime import datetime
from urllib.parse import quote

def collect(username: str):
    signals = []
    try:
        query = quote(f"{username} site:linkedin.com/in")
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": "identity-leak-bot/0.1"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200 and "linkedin.com/in" in resp.text:
            signals.append({
                "value": username,
                "confidence": 0.7,
                "signal_type": "INFERENCE",
                "evidence": "LinkedIn profile found via Google search",
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat()
            })
    except Exception as e:
        print(f"[!] LinkedIn plugin error for {username}: {e}")
    return signals
