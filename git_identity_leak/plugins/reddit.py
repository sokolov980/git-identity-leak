import requests


def collect(username):
    url = f"https://www.reddit.com/user/{username}.json"
    headers = {"User-Agent": "git-identity-leak"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            raise Exception("No Reddit data")

        return [{
            "signal_type": "POST_PLATFORM",
            "value": "Reddit activity detected",
            "confidence": "MEDIUM"
        }]

    except Exception:
        return [{
            "signal_type": "POST_PLATFORM",
            "value": "No Reddit posts detected",
            "confidence": "LOW"
        }]
