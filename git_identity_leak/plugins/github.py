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
    api_headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "git-identity-leak"
    } if token else {
        "User-Agent": "git-identity-leak"
    }

    def get_all_users(url):
        users = set()
        page = 1
        while True:
            r = requests.get(
                f"{url}?per_page=100&page={page}",
                headers=api_headers,
                timeout=10
            )
            if r.status_code != 200 or not r.json():
                break
            for u in r.json():
                if "login" in u:
                    users.add(u["login"])
            page += 1
        return users

    try:
        # ---------------- BASIC PROFILE ----------------
        r = requests.get(
            f"https://api.github.com/users/{username}",
            headers=api_headers,
            timeout=10
        )
        if r.status_code != 200:
            return signals

        data = r.json()

        profile_fields = [
            ("name", "NAME", "HIGH"),
            ("login", "USERNAME", "HIGH"),
            ("avatar_url", "IMAGE", "HIGH"),
            ("bio", "BIO", "MEDIUM"),
            ("email", "EMAIL", "HIGH"),
            ("company", "COMPANY", "MEDIUM"),
            ("location", "LOCATION", "MEDIUM"),
            ("blog", "URL", "MEDIUM"),
        ]

        for field, stype, conf in profile_fields:
            if data.get(field):
                signals.append({
                    "signal_type": stype,
                    "value": data[field],
                    "confidence": conf,
                    "source": "GitHub",
                    "collected_at": collected_at,
                })

        for f in ["followers", "following", "public_repos"]:
            signals.append({
                "signal_type": f.upper(),
                "value": str(data.get(f, 0)),
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at,
            })

        # ---------------- FOLLOW NETWORK ----------------
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

        # ---------------- CONTRIBUTIONS ----------------
        contrib_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Accept": "text/html,application/xhtml+xml"
        }

        contrib_url = f"https://github.com/users/{username}/contributions"
        contrib_resp = requests.get(contrib_url, headers=contrib_headers, timeout=10)

        yearly = {}
        weekday_count = 0
        weekend_count = 0
        daily_contribs = []

        if contrib_resp.status_code == 200:
            soup = BeautifulSoup(contrib_resp.text, "html.parser")

            for rect in soup.find_all("rect"):
                date = rect.get("data-date")
                count = rect.get("data-count")

                if not date or count is None:
                    continue

                count = int(count)
                daily_contribs.append({"date": date, "count": count})

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
            "collected_at": collected_at,
        })

        signals.append({
            "signal_type": "CONTRIBUTION_TIME_PATTERN",
            "value": f"Weekdays: {weekday_count}, Weekends: {weekend_count}",
            "confidence": "MEDIUM",
            "source": "GitHub",
            "collected_at": collected_at,
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

        if daily_contribs:
            signals.append({
                "signal_type": "CONTRIBUTIONS_YEARLY_DATES",
                "value": daily_contribs,
                "confidence": "HIGH",
                "source": "GitHub contributions page",
                "collected_at": collected_at,
            })

        # ---------------- REPOS + LANGUAGES ----------------
        repos_resp = requests.get(
            data["repos_url"],
            headers=api_headers,
            timeout=10
        )

        language_counter = Counter()

        if repos_resp.status_code == 200:
            for repo in repos_resp.json():
                name = repo.get("name")
                stars = repo.get("stargazers_count", 0)
                desc = (repo.get("description") or "").replace("\n", " ").strip()
                lang = repo.get("language") or "Unknown"
                updated = repo.get("updated_at", "").split("T")[0]

                language_counter[lang] += 1

                risk = "UNKNOWN"
                try:
                    days = (now - datetime.strptime(updated, "%Y-%m-%d")).days
                    if days < 90:
                        risk = "LOW"
                    elif days < 365:
                        risk = "MEDIUM"
                    else:
                        risk = "HIGH"
                except Exception:
                    pass

                signals.append({
                    "signal_type": "REPO_SUMMARY",
                    "value": f"{name} | Stars: {stars} | {desc} | Lang: {lang} | Last Updated: {updated}",
                    "confidence": "HIGH",
                    "source": "GitHub",
                    "collected_at": collected_at,
                })

        if language_counter:
            total = sum(language_counter.values())
            profile = ", ".join(
                f"{k} {int((v/total)*100)}%" for k, v in language_counter.most_common()
            )
            signals.append({
                "signal_type": "LANGUAGE_PROFILE",
                "value": profile,
                "confidence": "HIGH",
                "source": "GitHub",
                "collected_at": collected_at,
            })

    except Exception as e:
        print(f"[!] GitHub plugin error: {e}")

    return signals
