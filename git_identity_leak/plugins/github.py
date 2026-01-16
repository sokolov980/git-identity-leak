# git_identity_leak/plugins/github.py
import requests
from datetime import datetime
from bs4 import BeautifulSoup  

def collect(username):
    """
    Collect GitHub OSINT signals for a given username.
    Includes:
    - Basic profile info: name, username, avatar, bio, email, followers, following, public repos
    - Profile README if exists
    - Repo info: combined REPO_SUMMARY with stars, description, language, last updated, README URL
    - Contributions per year (scraped from contributions calendar)
    - Location, company, website, pronouns, social links, ORCID iD, achievements
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

        # Bio, email, company, location, website, pronouns
        for field in ["bio", "email", "company", "location", "blog", "twitter_username"]:
            if data.get(field):
                key = field.upper() if field != "blog" else "URL"
                if field == "twitter_username":
                    key = "SOCIAL_TWITTER"
                    value = f"https://twitter.com/{data[field]}"
                else:
                    value = data[field]
                signals.append({
                    "signal_type": key,
                    "value": value,
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at
                })

        # --- Profile README ---
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

        # --- Contributions per year ---
        contrib_url = f"https://github.com/users/{username}/contributions"
        try:
            r = requests.get(contrib_url, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                years = {}
                for rect in soup.find_all("rect", {"class": "ContributionCalendar-day"}):
                    date = rect.get("data-date")
                    count = int(rect.get("data-count", "0"))
                    if date:
                        year = date.split("-")[0]
                        years[year] = years.get(year, 0) + count
                for year, total in sorted(years.items(), reverse=True):
                    signals.append({
                        "signal_type": "CONTRIBUTIONS",
                        "value": f"{year}: {total}",
                        "confidence": "MEDIUM",
                        "source": "GitHub",
                        "collected_at": collected_at
                    })
        except Exception:
            pass

        # --- Repositories ---
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

        # --- Achievements / badges ---
        achievements_url = f"https://github.com/{username}?tab=achievements"
        try:
            r = requests.get(achievements_url, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                badges = [b.get("alt") for b in soup.find_all("img", {"class": "achievement-badge"}) if b.get("alt")]
                for badge in badges:
                    signals.append({
                        "signal_type": "BADGE",
                        "value": badge,
                        "confidence": "MEDIUM",
                        "source": "GitHub",
                        "collected_at": collected_at
                    })
        except Exception:
            pass

    except Exception as e:
        print(f"[!] GitHub plugin error for user {username}: {e}")

    return signals
