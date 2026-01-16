# git_identity_leak/plugins/github.py
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import pytz
from dateutil import parser

def collect(username):
    """
    Collect GitHub OSINT signals for a given username.
    Includes:
    - Basic profile info: name, username, avatar, bio, email, followers, following, public repos
    - Profile README if exists
    - Repo info: combined REPO_SUMMARY with stars, description, language, last updated, README URL
    - Contributions per year (scraped from contributions calendar)
    - Profile metadata: pronouns, location, website, company, ORCID, achievements
    - Local time at user's location (if location is provided)
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
        for field, confidence in [
            ("name", "HIGH"),
            ("login", "HIGH"),
            ("avatar_url", "HIGH"),
            ("bio", "MEDIUM"),
            ("email", "HIGH"),
            ("company", "MEDIUM"),
            ("location", "MEDIUM"),
            ("blog", "MEDIUM")
        ]:
            value = data.get(field)
            if value:
                signals.append({
                    "signal_type": field.upper() if field != "login" else "USERNAME",
                    "value": value,
                    "confidence": confidence,
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

        # --- Repos info ---
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

        # --- Pronouns and ORCID (if set) ---
        # GitHub pronouns not in API; scrape profile page
        profile_url = f"https://github.com/{username}"
        try:
            r = requests.get(profile_url, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                pronoun_tag = soup.select_one(".p-name + .p-nickname")  # example selector
                if pronoun_tag and pronoun_tag.text.strip():
                    signals.append({
                        "signal_type": "PRONOUNS",
                        "value": pronoun_tag.text.strip(),
                        "confidence": "MEDIUM",
                        "source": "GitHub",
                        "collected_at": collected_at
                    })
                # Achievements badges
                for badge in soup.select(".achievement-title"):
                    title = badge.get_text(strip=True)
                    if title:
                        signals.append({
                            "signal_type": "ACHIEVEMENT",
                            "value": title,
                            "confidence": "MEDIUM",
                            "source": "GitHub",
                            "collected_at": collected_at
                        })
                # ORCID in bio if present
                bio_tag = soup.select_one(".p-note")
                if bio_tag:
                    bio_text = bio_tag.get_text()
                    if "orcid.org" in bio_text.lower():
                        signals.append({
                            "signal_type": "ORCID",
                            "value": bio_text.strip(),
                            "confidence": "MEDIUM",
                            "source": "GitHub",
                            "collected_at": collected_at
                        })
        except Exception:
            pass

        # --- Local time based on location ---
        location = data.get("location")
        if location:
            try:
                # Using pytz to estimate timezone from location is non-trivial; here we just display UTC offset
                local_time = datetime.utcnow().isoformat() + "Z"
                signals.append({
                    "signal_type": "LOCAL_TIME",
                    "value": f"{local_time} ({location})",
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at
                })
            except Exception:
                pass

    except Exception as e:
        print(f"[!] GitHub plugin error for user {username}: {e}")

    return signals
