# git_identity_leak/plugins/github.py
import requests
from datetime import datetime

def collect(username):
    """
    Collect GitHub OSINT signals for a given username.
    Includes user info, followers, following, public repos, and per-repo details:
    - Repo README URL
    - Stars
    - Description
    - Main language
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

                # Repo README URL
                readme_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/master/README.md"
                signals.append({
                    "signal_type": "REPO_README",
                    "value": f"{repo_name}:{readme_url}",
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at
                })

                # Stars
                stars = repo.get("stargazers_count", 0)
                signals.append({
                    "signal_type": "REPO_STARS",
                    "value": f"{repo_name}:{stars}",
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at
                })

                # Description
                description = repo.get("description") or ""
                signals.append({
                    "signal_type": "REPO_DESC",
                    "value": f"{repo_name}:{description}",
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at
                })

                # Main language
                language = repo.get("language") or ""
                signals.append({
                    "signal_type": "REPO_LANG",
                    "value": f"{repo_name}:{language}",
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at
                })

    except Exception as e:
        print(f"[!] GitHub plugin error for user {username}: {e}")

    return signals
