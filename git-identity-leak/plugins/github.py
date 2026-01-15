# plugins/github.py

import requests

def collect(username):
    """
    Collect GitHub OSINT signals: profile name, avatar, email (if public), and repo images.
    """
    signals = []
    base_url = f"https://api.github.com/users/{username}"

    try:
        resp = requests.get(base_url)
        if resp.status_code != 200:
            print(f"[!] GitHub user {username} not found")
            return signals

        data = resp.json()
        # Name
        if data.get("name"):
            signals.append({"signal_type": "NAME", "value": data["name"], "confidence": "HIGH", "source": "GitHub"})
        # Avatar
        if data.get("avatar_url"):
            signals.append({"signal_type": "IMAGE", "value": data["avatar_url"], "confidence": "HIGH", "source": "GitHub"})
        # Email
        if data.get("email"):
            signals.append({"signal_type": "EMAIL", "value": data["email"], "confidence": "HIGH", "source": "GitHub"})
        # Repository images (README images)
        repos_url = data.get("repos_url")
        if repos_url:
            repos_resp = requests.get(repos_url)
            if repos_resp.status_code == 200:
                for repo in repos_resp.json():
                    readme_url = f"https://raw.githubusercontent.com/{username}/{repo['name']}/master/README.md"
                    signals.append({"signal_type": "REPO_README", "value": readme_url, "confidence": "MEDIUM", "source": "GitHub"})
    except Exception as e:
        print(f"[!] Error collecting GitHub data: {e}")

    return signals
