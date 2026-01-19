# git_identity_leak/plugins/github.py
import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

GITHUB_GRAPHQL = "https://api.github.com/graphql"

def collect(username):
    signals = []
    collected_at = datetime.utcnow().isoformat() + "Z"

    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # --- 1) REST API for profile, followers, repos, etc ---
    try:
        r = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Basic profile
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
                        "source": "GitHub REST",
                        "collected_at": collected_at,
                    })
            # Followers / following counts
            for f in ["followers", "following", "public_repos"]:
                signals.append({
                    "signal_type": f.upper(),
                    "value": str(data.get(f, 0)),
                    "confidence": "HIGH",
                    "source": "GitHub REST",
                    "collected_at": collected_at,
                })

            # Followers / following usernames
            def get_all_users(url):
                users = set()
                page = 1
                while True:
                    resp = requests.get(f"{url}?per_page=100&page={page}", headers=headers, timeout=10)
                    if resp.status_code != 200 or not resp.json():
                        break
                    for u in resp.json():
                        login = u.get("login")
                        if login:
                            users.add(login)
                    page += 1
                return users

            followers = get_all_users(f"https://api.github.com/users/{username}/followers")
            following = get_all_users(f"https://api.github.com/users/{username}/following")

            for u in sorted(followers - following):
                signals.append({"signal_type": "FOLLOWER_USERNAME","value": u,"confidence":"MEDIUM","source":"GitHub REST","collected_at":collected_at})
            for u in sorted(following - followers):
                signals.append({"signal_type": "FOLLOWING_USERNAME","value": u,"confidence":"MEDIUM","source":"GitHub REST","collected_at":collected_at})
            for u in sorted(followers & following):
                signals.append({"signal_type": "MUTUAL_CONNECTION","value": u,"confidence":"HIGH","source":"GitHub REST","collected_at":collected_at})

            # Repos
            repos_resp = requests.get(data["repos_url"], headers=headers, timeout=10)
            if repos_resp.status_code == 200:
                for repo in repos_resp.json():
                    repo_name = repo.get("name")
                    description = repo.get("description") or ""
                    stars = repo.get("stargazers_count",0)
                    language = repo.get("language") or "Unknown"
                    updated = repo.get("updated_at","").split("T")[0]
                    risk = "LOW"
                    try:
                        dt = datetime.strptime(updated, "%Y-%m-%d")
                        days_since = (datetime.utcnow() - dt).days
                        if days_since > 365:
                            risk = "HIGH"
                        elif days_since > 90:
                            risk = "MEDIUM"
                    except:
                        pass
                    readme_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/master/README.md"
                    signals.append({
                        "signal_type": "REPO_SUMMARY",
                        "value": f"{repo_name} | Stars: {stars} | {description} | Lang: {language} | Last Updated: {updated} | Inactivity: {risk} | README: {readme_url}",
                        "confidence": "HIGH",
                        "source": "GitHub REST",
                        "collected_at": collected_at,
                    })
                    signals.append({
                        "signal_type": "INACTIVITY_SCORE",
                        "value": f"{repo_name}: {risk}",
                        "confidence": "MEDIUM",
                        "source": "GitHub REST",
                        "collected_at": collected_at,
                    })
    except Exception as e:
        print("[!] REST API error:", e)

    # --- 2) GraphQL for contributions ---
    if token:
        try:
            headers_gql = {"Authorization": f"Bearer {token}", "Content-Type": "application/json","User-Agent":"git-identity-leak"}
            query = """
            query($login: String!) {
              user(login: $login) {
                contributionsCollection {
                  contributionCalendar {
                    totalContributions
                    weeks {
                      contributionDays {
                        date
                        contributionCount
                      }
                    }
                  }
                }
              }
            }"""
            r = requests.post(GITHUB_GRAPHQL, headers=headers_gql, json={"query":query,"variables":{"login":username}}, timeout=15)
            if r.status_code==200:
                data = r.json()
                calendar = data.get("data",{}).get("user",{}).get("contributionsCollection",{}).get("contributionCalendar",{})
                total = calendar.get("totalContributions",0)
                signals.append({
                    "signal_type":"CONTRIBUTION_TOTAL",
                    "value": str(total),
                    "confidence":"HIGH",
                    "source":"GitHub GraphQL",
                    "collected_at":collected_at
                })
                daily=[]
                weekday=0
                weekend=0
                yearly={}
                for week in calendar.get("weeks",[]):
                    for day in week.get("contributionDays",[]):
                        date=day["date"]
                        count=day["contributionCount"]
                        daily.append({"date":date,"count":count})
                        dt = datetime.strptime(date,"%Y-%m-%d")
                        year = str(dt.year)
                        yearly[year]=yearly.get(year,0)+count
                        if dt.weekday()<5:
                            weekday+=count
                        else:
                            weekend+=count
                signals.append({
                    "signal_type":"CONTRIBUTION_TIME_PATTERN",
                    "value":f"Weekdays: {weekday}, Weekends: {weekend}",
                    "confidence":"MEDIUM",
                    "source":"GitHub GraphQL",
                    "collected_at":collected_at
                })
                for year,count in yearly.items():
                    signals.append({
                        "signal_type":"CONTRIBUTIONS_YEAR",
                        "value":year,
                        "confidence":"HIGH",
                        "source":"GitHub GraphQL",
                        "collected_at":collected_at,
                        "meta":{"year":year,"count":count}
                    })
                signals.append({
                    "signal_type":"CONTRIBUTIONS_YEARLY_DATES",
                    "value":daily,
                    "confidence":"HIGH",
                    "source":"GitHub GraphQL",
                    "collected_at":collected_at
                })
        except Exception as e:
            print("[!] GraphQL contributions error:", e)

    return signals
