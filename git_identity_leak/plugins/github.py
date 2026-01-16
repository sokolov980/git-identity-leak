# git_identity_leak/plugins/github.py
import requests
from datetime import datetime

def collect(username):
    """
    Collect GitHub OSINT signals for a given username.
    Uses only the GitHub REST API v3.
    Includes:
    - Basic profile info: name, username, avatar, bio, email, company, location, blog
    - Followers, following, public repos
    - Repo info: combined REPO_SUMMARY with stars, description, language, last updated, README URL
    """
    signals = []
    collected_at = datetime.utcnow().isoformat() + "Z"

    user_url = f"https://api.github.com/users/{username}"
    try:
        r = requests.get(user_url, timeout=10)
        if r.status_code != 200:
            return signals
        data = r.json()

        # --- Basic profile info ---
        for field, signal_name, confidence in [
            ("name", "NAME", "HIGH"),
            ("login", "USERNAME", "HIGH"),
            ("avatar_url", "IMAGE", "HIGH"),
            ("bio", "BIO", "MEDIUM"),
            ("email", "EMAIL", "HIGH"),
            ("company", "COMPANY", "MEDIUM"),
            ("location", "LOCATION", "MEDIUM"),
            ("blog", "URL", "MEDIUM")
        ]:
            value = data.get(field)
            if value:
                signals.append({
                    "signal_type": signal_name,
                    "value": value,
                    "confidence": confidence,
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

        # --- Profile README detection ---
        profile_readme_url = f"https://raw.githubusercontent.com/{username}/{username}/master/README.md"
        try:
            resp = requests.head(profile_readme_url, timeout=5)
            if resp.status_code == 200:
                signals.append({
                    "signal_type": "PROFILE_README",
                    "value": profile_readme_url,
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at
                })
        except Exception:
            pass

        # --- Repo info ---
        repos_url = data.get("repos_url")
        if repos_url:
            repos = requests.get(repos_url, timeout=10).json()
            for repo in repos:
                repo_name = repo.get("name", "unknown")
                stars = repo.get("stargazers_count", 0)
                description = repo.get("description") or ""
                language = repo.get("language") or ""
                updated_at = repo.get("updated_at", "unknown").split("T")[0]
                readme_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/master/README.md"

                summary = (
                    f"{repo_name} | Stars: {stars} | {description} | "
                    f"Lang: {language} | Last Updated: {updated_at} | README: {readme_url}"
                )

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
