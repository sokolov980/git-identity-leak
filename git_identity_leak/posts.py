import requests
from datetime import datetime

# Public post sources
POST_SOURCES = {
    "Reddit": "https://www.reddit.com/user/{}/submitted.json",
    "StackOverflow": "https://api.stackexchange.com/2.3/users?inname={}&site=stackoverflow"
}

def analyze_posts(username: str):
    signals = []

    # Reddit
    reddit_url = POST_SOURCES["Reddit"].format(username)
    try:
        r = requests.get(reddit_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            for item in data.get("data", {}).get("children", []):
                signals.append({
                    "content": item["data"].get("title") or item["data"].get("selftext"),
                    "confidence": 0.7,
                    "evidence": item["data"].get("permalink"),
                    "first_seen": datetime.utcfromtimestamp(item["data"].get("created_utc")).isoformat(),
                    "last_seen": datetime.utcfromtimestamp(item["data"].get("created_utc")).isoformat()
                })
    except requests.RequestException:
        pass

    # StackOverflow
    so_url = POST_SOURCES["StackOverflow"].format(username)
    try:
        r = requests.get(so_url, timeout=5)
        if r.status_code == 200:
            items = r.json().get("items", [])
            for item in items:
                signals.append({
                    "content": item.get("display_name"),
                    "confidence": 0.6,
                    "evidence": f"https://stackoverflow.com/users/{item.get('user_id')}",
                    "first_seen": datetime.utcfromtimestamp(item.get("creation_date")).isoformat() if item.get("creation_date") else None,
                    "last_seen": datetime.utcfromtimestamp(item.get("last_access_date")).isoformat() if item.get("last_access_date") else None
                })
    except requests.RequestException:
        pass

    return signals
