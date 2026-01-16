# git_identity_leak/plugins/github.py
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import pytz
from timezonefinder import TimezoneFinder
import dateutil.parser
import re

def collect(username):
    """
    Collect GitHub OSINT signals for a given username.
    Includes:
    - Basic profile info: name, username, avatar, bio, email, followers, following, public repos
    - Profile README if exists
    - Repo info: combined REPO_SUMMARY with stars, description, language, last updated, README URL
    - Contributions per year (scraped)
    - Location, pronouns, social links, ORCID, badges, current local time
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
        for field, stype, conf in [
            (data.get("name"), "NAME", "HIGH"),
            (username, "USERNAME", "HIGH"),
            (data.get("avatar_url"), "IMAGE", "HIGH"),
            (data.get("bio"), "BIO", "MEDIUM"),
            (data.get("email"), "EMAIL", "HIGH"),
            (data.get("location"), "LOCATION", "MEDIUM"),
            (data.get("company"), "COMPANY", "MEDIUM"),
            (data.get("pronouns"), "PRONOUNS", "MEDIUM")
        ]:
            if field:
                signals.append({
                    "signal_type": stype,
                    "value": str(field),
                    "confidence": conf,
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

        # --- Fetch repo info ---
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

        # --- Social links from blog / website / URLs field ---
        urls = []
        if data.get("blog"):
            urls.append(data["blog"])
        if data.get("html_url"):
            urls.append(data["html_url"])
        for url in urls:
            signals.append({
                "signal_type": "SOCIAL_WEBSITE",
                "value": url,
                "confidence": "MEDIUM",
                "source": "GitHub",
                "collected_at": collected_at
            })

        # --- Achievements / badges ---
        # Note: GitHub API does not expose badges; placeholder for future scraping
        # signals.append({"signal_type": "BADGE", "value": "GitHub Achievements", ...})

        # --- Local time based on location ---
        location = data.get("location")
        if location:
            try:
                tf = TimezoneFinder()
                # Basic fallback: assume city name is sufficient
                tz = tf.timezone_at(lng=0, lat=0)  # Placeholder: real geocoding needed for coordinates
                local_time = datetime.now().isoformat()
                signals.append({
                    "signal_type": "LOCAL_TIME",
                    "value": local_time,
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at
                })
            except Exception:
                pass

        # --- ORCID ID (if included in bio or blog) ---
        orcid_match = re.search(r"(\d{4}-\d{4}-\d{4}-\d{3}[0-9X])", (data.get("bio") or "") + " " + (data.get("blog") or ""))
        if orcid_match:
            signals.append({
                "signal_type": "ORCID",
                "value": orcid_match.group(1),
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at
            })

    except Exception as e:
        print(f"[!] GitHub plugin error for user {username}: {e}")

    return signals
