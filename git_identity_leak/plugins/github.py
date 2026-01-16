import requests

def collect(username):
    """Collect GitHub profile info including avatar and repo README images"""
    signals = []

    user_api = f"https://api.github.com/users/{username}"
    try:
        r = requests.get(user_api, timeout=10)
        r.raise_for_status()
        data = r.json()

        # Real name
        if data.get("name"):
            signals.append({"signal_type": "NAME", "value": data["name"], "confidence": "HIGH"})

        # Avatar
        if data.get("avatar_url"):
            signals.append({"signal_type": "IMAGE", "value": data["avatar_url"], "confidence": "HIGH"})

        # Email (if public)
        if data.get("email"):
            signals.append({"signal_type": "EMAIL", "value": data["email"], "confidence": "MEDIUM"})

        # Repo README images
        repos_url = data.get("repos_url")
        if repos_url:
            r2 = requests.get(repos_url, timeout=10)
            r2.raise_for_status()
            for repo in r2.json():
                readme_url = f"https://raw.githubusercontent.com/{username}/{repo['name']}/master/README.md"
                signals.append({"signal_type": "REPO_README", "value": readme_url, "confidence": "MEDIUM"})

    except Exception as e:
        print(f"[!] Error collecting GitHub data for {username}: {e}")

    return signals
