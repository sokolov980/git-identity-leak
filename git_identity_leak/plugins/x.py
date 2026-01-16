import requests
from bs4 import BeautifulSoup

def collect(username):
    """Scrape public X posts using Nitter alternative or X HTML parsing"""
    signals = []
    try:
        url = f"https://nitter.net/{username}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        tweets = soup.find_all("div", class_="timeline-item")
        for tweet in tweets[:10]:
            text = tweet.find("p", class_="tweet-content")
            if text:
                signals.append({"signal_type": "POST_PLATFORM", "value": text.get_text(strip=True), "confidence": "MEDIUM"})
    except Exception as e:
        signals.append({"signal_type": "POST_PLATFORM", "value": f"Error collecting X posts: {e}", "confidence": "LOW"})
    return signals
