# git_identity_leak/plugins/x.py
import requests
from bs4 import BeautifulSoup

def collect(username):
    """
    Collect public posts from X (formerly Twitter) using Nitter.
    Returns a list of signal dicts with post content and timestamp.
    """
    signals = []
    nitter_url = f"https://nitter.net/{username}"

    try:
        response = requests.get(nitter_url, timeout=10, headers={"User-Agent": "git-identity-leak-osint/1.0"})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        posts = soup.find_all("div", class_="timeline-item")

        if not posts:
            signals.append({
                "signal_type": "POST_PLATFORM",
                "value": "No X posts detected",
                "confidence": "LOW"
            })
        else:
            for post in posts[:10]:  # Limit to latest 10 posts
                content_div = post.find("div", class_="tweet-content")
                timestamp_tag = post.find("a", class_="tweet-date")
                text = content_div.get_text(strip=True) if content_div else "N/A"
                timestamp = timestamp_tag["title"] if timestamp_tag and timestamp_tag.has_attr("title") else "N/A"
                signals.append({
                    "signal_type": "POST_X",
                    "value": f"{timestamp}: {text}",
                    "confidence": "MEDIUM"
                })

    except requests.exceptions.RequestException:
        # Handle SSL or connection errors gracefully
        signals.append({
            "signal_type": "POST_X",
            "value": f"Unable to collect X posts for {username}",
            "confidence": "LOW"
        })

    return signals
