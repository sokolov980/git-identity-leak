# git_identity_leak/plugins/github.py
import requests
from datetime import datetime

def collect(username):
    """
    Collect GitHub OSINT signals for a given username.
    Includes user info, followers, following, public repos, and per-repo details:
    - Combined REPO_SUMMARY for each repo with:
        - Stars
        - Description
        - Main language
        - README URL
    """
    signals = []
    collected_at = datetime.utcnow().isoformat() + "Z"

    user_url = f"https://api.github.com/users/{username}"
    try:
        r = requests.get(user_url, timeout=10)
        if r.status_code != 200:
            return signals
        data = r.json()

        # --- Basic user info ---
        if data.get("name"):
            signals.append({
                "signal_type": "NAME",
                "value": data["name"],
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at
            })

        signals.append({
            "signal_type": "USERNAME",
            "value": username,
            "confidence": "HIGH",
            "source": "GitHub",
            "collected_at": collected_at
        })

        if data.get("avatar_url"):
            signals.append({
                "signal_type": "IMAGE",
                "value": data["avatar_url"],
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at
            })

        if data.get("bio"):
            signals.append({
                "signal_type": "BIO",
                "value": data["bio"],
                "confidence": "MEDIUM",
                "source": "GitHub",
                "collected_at": collected_at
            })

        if data.get("email"):
            signals.append({
                "signal_type": "EMAIL",
                "value": data["email"],
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at
            })

        # --- Followers, following, public repos ---
        for field in ["followers", "following", "public_repos"]:
            if data.get(field) is not None:
                signals.append({
                    "signal_type": field.upper(),
                    "value": str(data[field]),
                    "confidence": "HIGH",
                    "source": "GitHub",
                    "collected_at": collected_at
                })

        # --- Fetch repos info ---
        repos_url = data.get("repos_url")
        if repos_url:
            repos = requests.get(repos_url, timeout=10).json()
            for repo in repos:
                repo_name = repo.get("name", "unknown")
                stars = repo.get("stargazers_count", 0)
                description = repo.get("description") or ""
                language = repo.get("language") or ""
                readme_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/master/README.md"

                # Combine all repo info into one signal
                summary = f"{repo_name} | Stars: {stars} | {description} | Lang: {language} | README: {readme_url}"

                signals.append({
                    "signal_type": "REPO_SUMMARY",
                    "value": summary,
                    "confidence": "HIGH",
                    "source": "GitHub",
                    "collected_at": collected_at
                })

    except Exception as e:
        print(f"[!] GitHub plugin error for user {username}: {e}")

    return signals
