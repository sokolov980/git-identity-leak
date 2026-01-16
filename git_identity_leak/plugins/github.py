# git_identity_leak/plugins/github.py
import requests
from datetime import datetime

def collect(username):
    signals = []
    collected_at = datetime.utcnow().isoformat() + "Z"

    url = f"https://api.github.com/users/{username}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return signals
        data = r.json()

        # Basic user info
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

        # Followers, following, public repos
        for field in ["followers", "following", "public_repos"]:
            if data.get(field) is not None:
                signals.append({
                    "signal_type": field.upper(),
                    "value": str(data[field]),
                    "confidence": "HIGH",
                    "source": "GitHub",
                    "collected_at": collected_at
                })

        # Fetch repos info
        repos_url = data.get("repos_url")
        if repos_url:
            repos = requests.get(repos_url, timeout=10).json()
            for repo in repos:
                # Repo README
                readme_url = f"https://raw.githubusercontent.com/{username}/{repo['name']}/master/README.md"
                signals.append({
                    "signal_type": "REPO_README",
                    "value": readme_url,
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at
                })

                # Stars
                signals.append({
                    "signal_type": "REPO_STARS",
                    "value": f"{repo['name']}:{repo.get('stargazers_count', 0)}",
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at
                })

                # Repo description
                description = repo.get("description")
                if description:
                    signals.append({
                        "signal_type": "REPO_DESC",
                        "value": f"{repo['name']}: {description}",
                        "confidence": "MEDIUM",
                        "source": "GitHub",
                        "collected_at": collected_at
                    })

                # Main language
                language = repo.get("language")
                if language:
                    signals.append({
                        "signal_type": "REPO_LANG",
                        "value": f"{repo['name']}: {language}",
                        "confidence": "MEDIUM",
                        "source": "GitHub",
                        "collected_at": collected_at
                    })

    except Exception:
        pass

    return signals
