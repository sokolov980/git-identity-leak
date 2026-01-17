# git_identity_leak/plugins/github.py
import requests
from datetime import datetime
from collections import Counter
from bs4 import BeautifulSoup
import re

def collect(username):
    """
    Collect GitHub signals for a public username without requiring a token.
    Includes:
    - Profile info
    - Followers / Following usernames + mutuals
    - Contributions total, per year, weekday/weekend, hourly pattern
    - Repo info and inactivity
    - Language profile
    - GitHub Pages, pronouns, social links
    """
    signals = []
    collected_at = datetime.utcnow().isoformat() + "Z"
    now = datetime.utcnow()

    def get_all_users(url):
        """Paginate followers/following"""
        users = set()
        page = 1
        while True:
            resp = requests.get(f"{url}?per_page=100&page={page}", timeout=10)
            if resp.status_code != 200 or not resp.json():
                break
            for u in resp.json():
                login = u.get("login")
                if login:
                    users.add(login)
            page += 1
        return users

    try:
        # --- Basic profile info ---
        r = requests.get(f"https://api.github.com/users/{username}", timeout=10)
        if r.status_code != 200:
            return signals
        data = r.json()

        for field, signal_name, confidence in [
            ("name", "NAME", "HIGH"),
            ("login", "USERNAME", "HIGH"),
            ("avatar_url", "IMAGE", "HIGH"),
            ("bio", "BIO", "MEDIUM"),
            ("email", "EMAIL", "HIGH"),
            ("company", "COMPANY", "MEDIUM"),
            ("location", "LOCATION", "MEDIUM"),
            ("blog", "URL", "MEDIUM"),
        ]:
            value = data.get(field)
            if value:
                signals.append({
                    "signal_type": signal_name,
                    "value": value,
                    "confidence": confidence,
                    "source": "GitHub",
                    "collected_at": collected_at,
                })

        # --- Followers / Following counts ---
        for field in ["followers", "following", "public_repos"]:
            signals.append({
                "signal_type": field.upper(),
                "value": str(data.get(field, 0)),
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at,
            })

        # --- Followers / Following usernames + mutual connections ---
        followers = get_all_users(f"https://api.github.com/users/{username}/followers")
        following = get_all_users(f"https://api.github.com/users/{username}/following")

        for u in sorted(followers - following):
            signals.append({
                "signal_type": "FOLLOWER_USERNAME",
                "value": u,
                "confidence": "MEDIUM",
                "source": "GitHub",
                "collected_at": collected_at,
            })
        for u in sorted(following - followers):
            signals.append({
                "signal_type": "FOLLOWING_USERNAME",
                "value": u,
                "confidence": "MEDIUM",
                "source": "GitHub",
                "collected_at": collected_at,
            })
        for u in sorted(followers & following):
            signals.append({
                "signal_type": "MUTUAL_CONNECTION",
                "value": u,
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at,
            })

        # --- Profile README ---
        readme_url = f"https://raw.githubusercontent.com/{username}/{username}/master/README.md"
        try:
            if requests.head(readme_url, timeout=5).status_code == 200:
                signals.append({
                    "signal_type": "PROFILE_README",
                    "value": readme_url,
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at,
                })
                readme_text = requests.get(readme_url, timeout=10).text
                soup_readme = BeautifulSoup(readme_text, "html.parser")
                for a in soup_readme.find_all("a", href=True):
                    href = a["href"]
                    for platform in ["twitter.com", "x.com", "linkedin.com", "reddit.com", "gitlab.com", "dev.to"]:
                        if platform in href:
                            signals.append({
                                "signal_type": "PROFILE_PLATFORM",
                                "value": href,
                                "confidence": "MEDIUM",
                                "source": "GitHub README",
                                "collected_at": collected_at
                            })
                match = re.search(r'(?i)pronouns?\s*[:\-]\s*([a-zA-Z/]+)', readme_text)
                if match:
                    signals.append({
                        "signal_type": "PRONOUNS",
                        "value": match.group(1),
                        "confidence": "MEDIUM",
                        "source": "GitHub README",
                        "collected_at": collected_at
                    })
        except Exception:
            pass

        # --- GitHub Pages detection ---
        gh_pages_url = f"https://{username}.github.io"
        try:
            if requests.head(gh_pages_url, timeout=5).status_code == 200:
                signals.append({
                    "signal_type": "GITHUB_PAGES",
                    "value": gh_pages_url,
                    "confidence": "HIGH",
                    "source": "GitHub",
                    "collected_at": collected_at
                })
        except Exception:
            pass

        # --- Contributions (scrape) ---
        yearly = {}
        weekday_count = 0
        weekend_count = 0
        contrib_resp = requests.get(f"https://github.com/users/{username}/contributions", timeout=10)
        if contrib_resp.status_code == 200:
            soup = BeautifulSoup(contrib_resp.text, "html.parser")
            for rect in soup.find_all("rect", class_="ContributionCalendar-day"):
                date = rect.get("data-date")
                count = int(rect.get("data-count", 0))
                if date:
                    dt = datetime.strptime(date, "%Y-%m-%d")
                    year = str(dt.year)
                    yearly[year] = yearly.get(year, 0) + count
                    if dt.weekday() < 5:
                        weekday_count += count
                    else:
                        weekend_count += count

        total_contribs = sum(yearly.values())
        signals.append({
            "signal_type": "CONTRIBUTION_TOTAL",
            "value": str(total_contribs),
            "confidence": "HIGH",
            "source": "GitHub",
            "collected_at": collected_at
        })
        signals.append({
            "signal_type": "CONTRIBUTION_TIME_PATTERN",
            "value": f"Weekdays: {weekday_count}, Weekends: {weekend_count}",
            "confidence": "MEDIUM",
            "source": "GitHub",
            "collected_at": collected_at
        })
        for year, count in sorted(yearly.items()):
            signals.append({
                "signal_type": "CONTRIBUTIONS_YEAR",
                "value": year,
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at,
                "meta": {"year": year, "count": count},
            })

        # --- Repo analysis and language profile ---
        repos_resp = requests.get(data["repos_url"], timeout=10)
        language_counter = Counter()
        if repos_resp.status_code == 200:
            for repo in repos_resp.json():
                repo_name = repo.get("name", "unknown")
                stars = repo.get("stargazers_count", 0)
                description = (repo.get("description") or "").replace("\n", " ").strip()
                language = repo.get("language") or "Unknown"
                updated_at = repo.get("updated_at", "").split("T")[0]

                language_counter[language] += 1

                # Repo inactivity
                risk = "UNKNOWN"
                try:
                    last_update = datetime.strptime(updated_at, "%Y-%m-%d")
                    days = (now - last_update).days
                    if days < 90:
                        risk = "LOW"
                    elif days < 365:
                        risk = "MEDIUM"
                    else:
                        risk = "HIGH"
                except Exception:
                    pass

                readme_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/master/README.md"
                signals.append({
                    "signal_type": "REPO_SUMMARY",
                    "value": f"{repo_name} | Stars: {stars} | {description} | Lang: {language} | Last Updated: {updated_at} | Inactivity: {risk} | README: {readme_url}",
                    "confidence": "HIGH",
                    "source": "GitHub",
                    "collected_at": collected_at,
                })
                signals.append({
                    "signal_type": "INACTIVITY_SCORE",
                    "value": f"{repo_name}: {risk}",
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at,
                })

        # --- Language profile ---
        if language_counter:
            total = sum(language_counter.values())
            profile = ", ".join(f"{lang} {int((count/total)*100)}%" for lang, count in language_counter.most_common())
            signals.append({
                "signal_type": "LANGUAGE_PROFILE",
                "value": profile,
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at,
                "meta": dict(language_counter),
            })

    except Exception as e:
        print(f"[!] GitHub plugin error: {e}")

    return signals
