import requests

PUBLIC_SITES = {
    "GitHub": "https://github.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "Bitbucket": "https://bitbucket.org/{}"
}

def check_username(username):
    results = []
    if not username:
        return results
    for site, url in PUBLIC_SITES.items():
        try:
            r = requests.get(url.format(username), timeout=5)
            found = r.status_code == 200
        except Exception:
            found = False
        confidence = "HIGH" if found else "LOW"
        results.append({"site": site, "found": found, "confidence": confidence})
    return results

def check_email(email):
    # Simple domain presence check; no scraping of private sources
    results = []
    if not email:
        return results
    # Placeholder: in Phase 3 we can expand to public forums or paste sites
    results.append({"site": "GitHub (noreply)", "found": email.endswith("@users.noreply.github.com"), "confidence": "MEDIUM"})
    return results
