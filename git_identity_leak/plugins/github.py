# git_identity_leak/plugins/github.py
import requests
from datetime import datetime

GITHUB_API_BASE = "https://api.github.com"

def collect(username):
    """
    Collect enriched GitHub OSINT signals for a given username.
    Returns a list of signals suitable for full_analysis().
    """
    signals = []
    collected_at = datetime.utcnow().isoformat() + "Z"

    try:
        # Fetch user profile
        user_url = f"{GITHUB_API_BASE}/users/{username}"
        r = requests.get(user_url, timeout=10)
        if r.status_code != 200:
            return signals
        user_data = r.json()

        # Basic profile info
        for key, signal_type, confidence in [
            ("name", "NAME", "HIGH"),
            ("login", "USERNAME", "HIGH"),
            ("avatar_url", "IMAGE", "HIGH"),
            ("bio", "BIO", "MEDIUM"),
            ("email", "EMAIL", "HIGH"),
        ]:
            val = user_data.get(key)
            if val:
                signals.append({
                    "signal_type": signal_type,
                    "value": str(val),
                    "confidence": confidence,
                    "source": "GitHub",
                    "collected_at": collected_at
                })

        # Followers / following / public repos
        for field in ["followers", "following", "public_repos"]:
            val = user_data.get(field)
            if val is not None:
                signals.append({
                    "signal_type": field.upper(),
                    "value": str(val),
                    "confidence": "HIGH",
                    "source": "GitHub",
                    "collected_at": collected_at
                })

        # Fetch repos
        repos_url = user_data.get("repos_url")
        if repos_url:
            repos = requests.get(repos_url, timeout=10).json()
            for repo in repos:
                # Repo stars
                stargazers = repo.get("stargazers_count")
                if stargazers is not None:
                    signals.append({
                        "signal_type": "REPO_STARS",
                        "value": f"{repo['name']}:{stargazers}",
                        "confidence": "MEDIUM",
                        "source": "GitHub",
                        "collected_at": collected_at
                    })

                # Repo README URL
                readme_url = f"https://raw.githubusercontent.com/{username}/{repo['name']}/master/README.md"
                signals.append({
                    "signal_type": "REPO_README",
                    "value": readme_url,
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at
                })

        # Optional: Contributions per year (requires scraping contributions graph)
        contrib_url = f"https://github.com/users/{username}/contributions"
        r = requests.get(contrib_url, timeout=10)
        if r.status_code == 200:
            from xml.etree import ElementTree as ET
            try:
                tree = ET.fromstring(r.text)
                yearly_counts = {}
                for rect in tree.findall(".//rect[@data-date]"):
                    date = rect.attrib["data-date"]
                    count = int(rect.attrib.get("data-count", 0))
                    year = date.split("-")[0]
                    yearly_counts[year] = yearly_counts.get(year, 0) + count
                for year, total in yearly_counts.items():
                    signals.append({
                        "signal_type": "CONTRIBUTIONS",
                        "value": f"{year}:{total}",
                        "confidence": "MEDIUM",
                        "source": "GitHub",
                        "collected_at": collected_at
                    })
            except Exception:
                pass

    except Exception:
        pass

    return signals
