# git_identity_leak/plugins/github.py

import os
import requests
from datetime import datetime
from collections import Counter
from bs4 import BeautifulSoup
import re

GITHUB_BASE = "https://api.github.com"

def collect(username):
    signals = []
    collected_at = datetime.utcnow().isoformat() + "Z"
    now = datetime.utcnow()

    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}

    def get_all_users(url):
        users = set()
        page = 1
        while True:
            r = requests.get(
                f"{url}?per_page=100&page={page}",
                headers=headers,
                timeout=10
            )
            if r.status_code != 200:
                break
            data = r.json()
            if not data:
                break
            for u in data:
                if u.get("login"):
                    users.add(u["login"])
            page += 1
        return users

    try:
        # ───────────────────────── BASIC PROFILE ─────────────────────────
        r = requests.get(f"{GITHUB_BASE}/users/{username}", headers=headers, timeout=10)
        if r.status_code != 200:
            return signals

        data = r.json()

        fields = [
            ("name", "NAME", "HIGH"),
            ("login", "USERNAME", "HIGH"),
            ("avatar_url", "IMAGE", "HIGH"),
            ("bio", "BIO", "MEDIUM"),
            ("email", "EMAIL", "HIGH"),
            ("company", "COMPANY", "MEDIUM"),
            ("location", "LOCATION", "MEDIUM"),
            ("blog", "URL", "MEDIUM"),
        ]

        for field, stype, conf in fields:
            if data.get(field):
                signals.append({
                    "signal_type": stype,
                    "value": data[field],
                    "confidence": conf,
                    "source": "GitHub",
                    "collected_at": collected_at,
                })

        for field in ["followers", "following", "public_repos"]:
            signals.append({
                "signal_type": field.upper(),
                "value": str(data.get(field, 0)),
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at,
            })

        # ───────────────────────── FOLLOW GRAPH ─────────────────────────
        followers = get_all_users(f"{GITHUB_BASE}/users/{username}/followers")
        following = get_all_users(f"{GITHUB_BASE}/users/{username}/following")

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

        # ───────────────────────── README / SOCIAL ─────────────────────────
        readme_url = f"https://raw.githubusercontent.com/{username}/{username}/master/README.md"
        try:
            if requests.head(readme_url, timeout=5).status_code == 200:
                text = requests.get(readme_url, timeout=10).text
                soup = BeautifulSoup(text, "html.parser")

                signals.append({
                    "signal_type": "PROFILE_README",
                    "value": readme_url,
                    "confidence": "MEDIUM",
                    "source": "GitHub",
                    "collected_at": collected_at,
                })

                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    for p in ["twitter.com", "x.com", "linkedin.com", "reddit.com", "gitlab.com", "dev.to"]:
                        if p in href:
                            signals.append({
                                "signal_type": "PROFILE_PLATFORM",
                                "value": href,
                                "confidence": "MEDIUM",
                                "source": "GitHub README",
                                "collected_at": collected_at,
                            })

                m = re.search(r'(?i)pronouns?\s*[:\-]\s*([a-zA-Z/]+)', text)
                if m:
                    signals.append({
                        "signal_type": "PRONOUNS",
                        "value": m.group(1),
                        "confidence": "MEDIUM",
                        "source": "GitHub README",
                        "collected_at": collected_at,
                    })
        except Exception:
            pass

        # ───────────────────────── CONTRIBUTIONS (FIXED) ─────────────────────────
        yearly = {}
        weekday_count = 0
        weekend_count = 0
        daily = []

        html = requests.get(
            f"https://github.com/users/{username}/contributions",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        if html.status_code == 200:
            soup = BeautifulSoup(html.text, "html.parser")
            for rect in soup.select("rect[data-date][data-count]"):
                date = rect["data-date"]
                count = int(rect["data-count"])

                daily.append({"date": date, "count": count})

                dt = datetime.strptime(date, "%Y-%m-%d")
                yearly.setdefault(str(dt.year), 0)
                yearly[str(dt.year)] += count

                if dt.weekday() < 5:
                    weekday_count += count
                else:
                    weekend_count += count

        total = sum(yearly.values())

        signals.append({
            "signal_type": "CONTRIBUTION_TOTAL",
            "value": str(total),
            "confidence": "HIGH",
            "source": "GitHub",
            "collected_at": collected_at,
        })

        signals.append({
            "signal_type": "CONTRIBUTION_TIME_PATTERN",
            "value": f"Weekdays: {weekday_count}, Weekends: {weekend_count}",
            "confidence": "MEDIUM",
            "source": "GitHub",
            "collected_at": collected_at,
        })

        for y, c in sorted(yearly.items()):
            signals.append({
                "signal_type": "CONTRIBUTIONS_YEAR",
                "value": y,
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at,
                "meta": {"year": y, "count": c},
            })

        if daily:
            signals.append({
                "signal_type": "CONTRIBUTIONS_YEARLY_DATES",
                "value": sorted(daily, key=lambda x: x["date"]),
                "confidence": "HIGH",
                "source": "GitHub contributions page",
                "collected_at": collected_at,
            })

        # ───────────────────────── REPOS / LANG / HOURLY ─────────────────────────
        repos = requests.get(data["repos_url"], headers=headers, timeout=10)
        language_counter = Counter()
        hourly = [0] * 24

        if repos.status_code == 200:
            for repo in repos.json():
                name = repo["name"]
                lang = repo.get("language") or "Unknown"
                stars = repo.get("stargazers_count", 0)
                updated = repo.get("updated_at", "").split("T")[0]

                language_counter[lang] += 1

                signals.append({
                    "signal_type": "REPO_SUMMARY",
                    "value": (
                        f"{name} | Stars: {stars} | "
                        f"Lang: {lang} | Last Updated: {updated}"
                    ),
                    "confidence": "HIGH",
                    "source": "GitHub",
                    "collected_at": collected_at,
                })

                commits = requests.get(
                    f"{GITHUB_BASE}/repos/{username}/{name}/commits?author={username}&per_page=100",
                    headers=headers,
                    timeout=10,
                )
                if commits.status_code == 200:
                    for c in commits.json():
                        dt = c.get("commit", {}).get("author", {}).get("date")
                        if dt:
                            hourly[datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ").hour] += 1

        if language_counter:
            total_lang = sum(language_counter.values())
            profile = ", ".join(
                f"{k} {int((v/total_lang)*100)}%"
                for k, v in language_counter.most_common()
            )
            signals.append({
                "signal_type": "LANGUAGE_PROFILE",
                "value": profile,
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at,
            })

        signals.append({
            "signal_type": "CONTRIBUTION_HOURLY_PATTERN",
            "value": {str(i): v for i, v in enumerate(hourly)},
            "confidence": "MEDIUM",
            "source": "GitHub commits",
            "collected_at": collected_at,
        })

    except Exception as e:
        print(f"[!] GitHub plugin error: {e}")

    return signals
