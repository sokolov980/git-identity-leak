# plugins/reddit.py

import requests

def collect(username):
    """
    Fetch public Reddit posts/comments for a username
    """
    signals = []
    try:
        url = f"https://www.reddit.com/user/{username}/submitted.json"
        headers = {"User-Agent": "git-identity-leak-bot"}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            posts = data.get("data", {}).get("children", [])
            if posts:
                signals.append({"signal_type": "POST_PLATFORM", "value": f"Reddit posts found ({len(posts)})", "confidence": "MEDIUM", "source": "Reddit"})
            else:
                signals.append({"signal_type": "POST_PLATFORM", "value": "No Reddit posts detected", "confidence": "LOW", "source": "Reddit"})
        else:
            signals.append({"signal_type": "POST_PLATFORM", "value": "No Reddit posts detected", "confidence": "LOW", "source": "Reddit"})
    except Exception as e:
        print(f"[!] Error collecting Reddit data: {e}")
    return signals
