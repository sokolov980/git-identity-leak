# plugins/linkedin.py

import requests
from bs4 import BeautifulSoup

def collect(username):
    """
    Attempt to collect public LinkedIn info based on profile URL
    """
    signals = []
    profile_url = f"https://www.linkedin.com/in/{username}"
    try:
        resp = requests.get(profile_url)
        if resp.status_code == 200:
            signals.append({"signal_type": "PROFILE_PLATFORM", "value": profile_url, "confidence": "MEDIUM", "source": "LinkedIn"})
        else:
            signals.append({"signal_type": "PROFILE_PLATFORM", "value": "No public LinkedIn profile detected", "confidence": "LOW", "source": "LinkedIn"})
    except Exception as e:
        print(f"[!] Error collecting LinkedIn data: {e}")
    return signals
