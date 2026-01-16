import requests

def collect(username):
    """Scrape public Reddit posts via Pushshift or old Reddit JSON endpoints"""
    signals = []
    try:
        url = f"https://www.reddit.com/user/{username}/submitted.json"
        r = requests.get(url, headers={"User-Agent": "OSINT-Tool"}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if "data" in data and "children" in data["data"]:
                for post in data["data"]["children"]:
                    signals.append({
                        "signal_type": "POST_PLATFORM",
                        "value": post["data"]["title"],
                        "confidence": "MEDIUM"
                    })
        else:
            signals.append({"signal_type": "POST_PLATFORM", "value": "No Reddit posts detected", "confidence": "LOW"})
    except Exception as e:
        signals.append({"signal_type": "POST_PLATFORM", "value": f"Error collecting Reddit posts: {e}", "confidence": "LOW"})
    return signals
