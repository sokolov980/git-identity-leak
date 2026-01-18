# git_identity_leak/plugins/github.py
import os
import requests
from datetime import datetime
from collections import Counter
from bs4 import BeautifulSoup
import re

def collect(username):
    signals = []
    collected_at = datetime.utcnow().isoformat() + "Z"
    now = datetime.utcnow()

    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}

    try:
        # ---------------- BASIC PROFILE ----------------
        r = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=10)
        if r.status_code != 200:
            return signals

        data = r.json()

        def add(sig, val, conf="HIGH", src="GitHub"):
            signals.append({
                "signal_type": sig,
                "value": val,
                "confidence": conf,
                "source": src,
                "collected_at": collected_at
            })

        for field, sig in [
            ("name", "NAME"),
            ("login", "USERNAME"),
            ("avatar_url", "IMAGE"),
            ("bio", "BIO"),
            ("company", "COMPANY"),
            ("location", "LOCATION"),
            ("blog", "URL"),
            ("email", "EMAIL"),
        ]:
            if data.get(field):
                add(sig, data[field])

        add("FOLLOWERS", str(data.get("followers", 0)))
        add("FOLLOWING", str(data.get("following", 0)))
        add("PUBLIC_REPOS", str(data.get("public_repos", 0)))

        # ---------------- CONTRIBUTIONS (SALLAR METHOD) ----------------
        profile_html = requests.get(f"https://github.com/{username}", timeout=10).text
        soup = BeautifulSoup(profile_html, "html.parser")

        daily_contribs = []
        yearly = {}
        weekday_count = 0
        weekend_count = 0

        for rect in soup.select("svg rect[data-date][data-count]"):
            date = rect.get("data-date")
            count = int(rect.get("data-count", 0))

            if not date:
                continue

            daily_contribs.append({"date": date, "count": count})

            dt = datetime.strptime(date, "%Y-%m-%d")
            year = str(dt.year)
            yearly[year] = yearly.get(year, 0) + count

            if dt.weekday() < 5:
                weekday_count += count
            else:
                weekend_count += count

        total_contribs = sum(yearly.values())

        add("CONTRIBUTION_TOTAL", str(total_contribs))
        add(
            "CONTRIBUTION_TIME_PATTERN",
            f"Weekdays: {weekday_count}, Weekends: {weekend_count}",
            "MEDIUM"
        )

        for year, count in sorted(yearly.items()):
            signals.append({
                "signal_type": "CONTRIBUTIONS_YEAR",
                "value": year,
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at,
                "meta": {"year": year, "count": count}
            })

        if daily_contribs:
            signals.append({
                "signal_type": "CONTRIBUTIONS_YEARLY_DATES",
                "value": daily_contribs,
                "confidence": "HIGH",
                "source": "GitHub profile page",
                "collected_at": collected_at
            })

        # ---------------- REPOS + LANGUAGES + HOURLY ----------------
        repos = requests.get(data["repos_url"], headers=headers, timeout=10).json()
        lang_counter = Counter()
        hourly = [0] * 24

        for repo in repos:
            name = repo.get("name")
            stars = repo.get("stargazers_count", 0)
            desc = (repo.get("description") or "").replace("\n", " ")
            lang = repo.get("language") or "Unknown"
            updated = repo.get("updated_at", "").split("T")[0]

            lang_counter[lang] += 1

            add(
                "REPO_SUMMARY",
                f"{name} | Stars: {stars} | {desc} | Lang: {lang} | Last Updated: {updated}",
            )

            commits = requests.get(
                f"https://api.github.com/repos/{username}/{name}/commits?author={username}&per_page=100",
                headers=headers,
                timeout=10
            )

            if commits.status_code == 200:
                for c in commits.json():
                    dt = c.get("commit", {}).get("author", {}).get("date")
                    if dt:
                        hour = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ").hour
                        hourly[hour] += 1

        if lang_counter:
            total = sum(lang_counter.values())
            profile = ", ".join(
                f"{l} {int((c/total)*100)}%" for l, c in lang_counter.most_common()
            )
            add("LANGUAGE_PROFILE", profile)

        add(
            "CONTRIBUTION_HOURLY_PATTERN",
            {str(i): v for i, v in enumerate(hourly)},
            "MEDIUM",
            "GitHub commits"
        )

    except Exception as e:
        print(f"[!] GitHub plugin error: {e}")

    return signals
