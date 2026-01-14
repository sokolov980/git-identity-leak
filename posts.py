import requests

# Minimal safe approach: check public user pages for username mentions
PUBLIC_POST_SITES = {
    "Reddit": "https://www.reddit.com/user/{}/",
    "StackOverflow": "https://stackoverflow.com/users/{}",
    "GitLab": "https://gitlab.com/{}"
}

def analyze_posts(username):
    results = []
    if not username:
        return results
    headers = {"User-Agent": "Mozilla/5.0"}
    for site, url in PUBLIC_POST_SITES.items():
        found = False
        try:
            r = requests.get(url.format(username), headers=headers, timeout=5)
            found = r.status_code == 200
        except Exception:
            found = False
        confidence = "HIGH" if found else "LOW"
        results.append({"site": site, "found": found, "confidence": confidence})
    return results
