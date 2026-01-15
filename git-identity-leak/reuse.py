# reuse.py

import requests

USERNAME_SITES = {
    "GitHub": "https://github.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "Bitbucket": "https://bitbucket.org/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "X": "https://nitter.net/{}",
    "LinkedIn": "https://www.linkedin.com/in/{}"
}

EMAIL_DOMAINS = {
    "GitHub (noreply)": "https://github.com/{}"  # placeholder for noreply detection
}

def check_username_reuse(username):
    """
    Check if the username exists across multiple platforms.
    Returns a list of results with confidence.
    """
    results = []
    for platform, url_template in USERNAME_SITES.items():
        try:
            url = url_template.format(username)
            resp = requests.head(url, allow_redirects=True, timeout=5)
            found = resp.status_code == 200
            confidence = "HIGH" if found else "LOW"
            results.append({"site": platform, "found": found, "confidence": confidence})
        except Exception:
            results.append({"site": platform, "found": False, "confidence": "LOW"})
    return results

def check_email_reuse(email):
    """
    Check if the email is associated with public accounts (limited check)
    """
    results = []
    for platform, url_template in EMAIL_DOMAINS.items():
        try:
            username = email.split("@")[0]
            url = url_template.format(username)
            resp = requests.head(url, allow_redirects=True, timeout=5)
            found = resp.status_code == 200
            confidence = "MEDIUM" if found else "LOW"
            results.append({"site": platform, "found": found, "confidence": confidence})
        except Exception:
            results.append({"site": platform, "found": False, "confidence": "LOW"})
    return results
