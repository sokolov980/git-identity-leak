import requests


def collect(username):
    signals = []

    url = f"https://api.github.com/users/{username}"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return signals

    data = r.json()

    if data.get("name"):
        signals.append({
            "signal_type": "NAME",
            "value": data["name"],
            "confidence": "HIGH"
        })

    if data.get("avatar_url"):
        signals.append({
            "signal_type": "IMAGE",
            "value": data["avatar_url"],
            "confidence": "HIGH"
        })

    repos_url = data.get("repos_url")
    if repos_url:
        repos = requests.get(repos_url, timeout=10).json()
        for repo in repos:
            readme = f"https://raw.githubusercontent.com/{username}/{repo['name']}/master/README.md"
            signals.append({
                "signal_type": "REPO_README",
                "value": readme,
                "confidence": "MEDIUM"
            })

    return signals
