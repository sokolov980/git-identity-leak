# git_identity_leak/plugins/github.py
import requests
from datetime import datetime
from collections import Counter
from bs4 import BeautifulSoup

def collect(username):
    signals = []
    collected_at = datetime.utcnow().isoformat() + "Z"
    now = datetime.utcnow()

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

        # --- Counts ---
        for field in ["followers", "following", "public_repos"]:
            signals.append({
                "signal_type": field.upper(),
                "value": str(data.get(field, 0)),
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at,
            })

        # --- Followers / Following usernames ---
        followers, following = set(), set()

        for rel, target in [("followers", followers), ("following", following)]:
            resp = requests.get(f"https://api.github.com/users/{username}/{rel}", timeout=10)
            if resp.status_code == 200:
                for u in resp.json():
                    if u.get("login"):
                        target.add(u["login"])

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
        if requests.head(readme_url, timeout=5).status_code == 200:
            signals.append({
                "signal_type": "PROFILE_README",
                "value": readme_url,
                "confidence": "MEDIUM",
                "source": "GitHub",
                "collected_at": collected_at,
            })

        # --- Contributions per year ---
        contrib_resp = requests.get(
            f"https://github.com/users/{username}/contributions",
            timeout=10
        )

        if contrib_resp.status_code == 200:
            soup = BeautifulSoup(contrib_resp.text, "html.parser")
            yearly = {}

            for rect in soup.find_all("rect", class_="ContributionCalendar-day"):
                date = rect.get("data-date")
                count = int(rect.get("data-count", 0))
                if date:
                    year = date.split("-")[0]
                    yearly[year] = yearly.get(year, 0) + count

            for year, total in sorted(yearly.items()):
                signals.append({
                    "signal_type": "CONTRIBUTIONS",
                    "value": f"{year}: {total}",
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at,
                })

                signals.append({
                    "signal_type": "CONTRIBUTIONS_YEAR",
                    "value": year,
                    "confidence": "HIGH",
                    "source": "GitHub",
                    "collected_at": collected_at,
                    "meta": {"year": year, "count": total},
                })

        # --- Repo analysis ---
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
                    "value": (
                        f"{repo_name} | Stars: {stars} | {description} | "
                        f"Lang: {language} | Last Updated: {updated_at} | "
                        f"Inactivity: {risk} | README: {readme_url}"
                    ),
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
            profile = ", ".join(
                f"{lang} {int((count / total) * 100)}%"
                for lang, count in language_counter.most_common()
            )
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
