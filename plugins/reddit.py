# git_identity_leak/plugins/reddit.py
import requests
from datetime import datetime

BASE_URL = "https://www.reddit.com/user"

HEADERS = {
    "User-Agent": "identity-leak-bot/0.1"
}

def collect(username: str):
    signals = []
    try:
        url = f"{BASE_URL}/{username}"
        resp = requests.get(url + ".json", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            posts = data.get("data", {}).get("children", [])
            for post in posts:
                signals.append({
                    "value": post["data"].get("title") or post["data"].get("selftext"),
                    "confidence": 0.5,
                    "signal_type": "INFERENCE",
                    "evidence": f"Reddit post in {post['data'].get('subreddit')}",
                    "first_seen": datetime.utcnow().isoformat(),
                    "last_seen": datetime.utcnow().isoformat()
                })

            # Signal that profile exists
            signals.append({
                "value": username,
                "confidence": 0.8,
                "signal_type": "FACT",
                "evidence": f"Reddit profile found at {url}",
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat()
            })
    except Exception as e:
        print(f"[!] Reddit plugin error for {username}: {e}")
    return signals
