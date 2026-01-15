import requests
from datetime import datetime

def collect(username: str):
    url = f"https://www.reddit.com/user/{username}/submitted.json"
    signals = []
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            for item in data.get("data", {}).get("children", []):
                signals.append({
                    "type": "post",
                    "value": item["data"].get("title") or item["data"].get("selftext"),
                    "confidence": 0.7,
                    "signal_type": "INFERENCE",
                    "evidence": f"https://reddit.com{item['data'].get('permalink')}",
                    "first_seen": datetime.utcfromtimestamp(item["data"]["created_utc"]).isoformat(),
                    "last_seen": datetime.utcfromtimestamp(item["data"]["created_utc"]).isoformat()
                })
    except requests.RequestException:
        pass
    return signals
