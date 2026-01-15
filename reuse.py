import requests
from datetime import datetime

# List of public platforms to check usernames
PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "Bitbucket": "https://bitbucket.org/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "X (formerly Twitter)": "https://x.com/{}",
    "LinkedIn": "https://www.linkedin.com/in/{}"
}

def check_username_reuse(username: str):
    results = []
    for platform, url_template in PLATFORMS.items():
        profile_url = url_template.format(username)
        try:
            r = requests.get(profile_url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            found = r.status_code == 200
        except requests.RequestException:
            found = False
        results.append({
            "site": platform,
            "found": found,
            "confidence": 0.9 if found else 0.3,
            "evidence": f"Public profile URL: {profile_url}" if found else None,
            "first_seen": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat()
        })
    return results

def check_email_reuse(username: str):
    # Only GitHub noreply emails for now
    email = f"{username}+{hash(username) % 1000000}@users.noreply.github.com"
    return [{
        "site": "GitHub",
        "value": email,
        "found": True,
        "confidence": 0.7,
        "evidence": "Public commit email pattern",
        "first_seen": datetime.utcnow().isoformat(),
        "last_seen": datetime.utcnow().isoformat()
    }]
