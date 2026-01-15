# git_identity_leak/plugins/github.py
from datetime import datetime
from git_identity_leak.github_api import fetch_user_info, fetch_user_repos

def collect(username: str):
    signals = []

    # Public profile info
    user_info = fetch_user_info(username)
    if user_info.get("name"):
        signals.append({
            "value": user_info["name"],
            "confidence": 0.8,
            "signal_type": "FACT",
            "evidence": "GitHub profile name",
            "first_seen": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat()
        })
    if user_info.get("email"):
        signals.append({
            "value": user_info["email"],
            "confidence": 0.7,
            "signal_type": "FACT",
            "evidence": "GitHub profile email",
            "first_seen": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat()
        })

    # Profile image
    if user_info.get("avatar_url"):
        signals.append({
            "value": user_info["avatar_url"],
            "confidence": 0.9,
            "signal_type": "IMAGE",
            "evidence": "GitHub profile avatar",
            "first_seen": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat()
        })

    # Images from repositories
    repos = fetch_user_repos(username)
    for repo in repos:
        for img_url in repo.get("image_urls", []):
            signals.append({
                "value": img_url,
                "confidence": 0.6,
                "signal_type": "IMAGE",
                "evidence": f"Repo {repo['name']}",
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat()
            })

    return signals
