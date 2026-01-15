# git_identity_leak/plugins/reddit.py
import requests

def collect(username):
    """
    Collect public posts from Reddit for a given username.
    Returns a list of signal dicts.
    """
    signals = []
    reddit_url = f"https://www.reddit.com/user/{username}/.json"
    headers = {"User-Agent": "git-identity-leak-osint/1.0"}

    try:
        response = requests.get(reddit_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        children = data.get("data", {}).get("children", [])
        if not children:
            signals.append({
                "signal_type": "POST_REDDIT",
                "value": "No Reddit posts detected",
                "confidence": "LOW"
            })
        else:
            for post in children[:10]:  # limit to 10 latest posts
                post_data = post.get("data", {})
                title = post_data.get("title") or post_data.get("selftext", "")
                subreddit = post_data.get("subreddit", "N/A")
                timestamp = post_data.get("created_utc", "N/A")
                signals.append({
                    "signal_type": "POST_REDDIT",
                    "value": f"{subreddit} | {timestamp}: {title}",
                    "confidence": "MEDIUM"
                })

    except requests.exceptions.RequestException:
        signals.append({
            "signal_type": "POST_REDDIT",
            "value": f"Unable to collect Reddit posts for {username}",
            "confidence": "LOW"
        })
    except ValueError:
        # JSON decode error
        signals.append({
            "signal_type": "POST_REDDIT",
            "value": f"Reddit data for {username} is malformed or unavailable",
            "confidence": "LOW"
        })

    return signals
