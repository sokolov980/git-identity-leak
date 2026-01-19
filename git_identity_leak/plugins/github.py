import os
import requests
from datetime import datetime

GITHUB_GRAPHQL = "https://api.github.com/graphql"

def collect(username):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[!] GITHUB_TOKEN not set — contributions cannot be fetched.")
        return []

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "git-identity-leak"
    }

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
    }
    """

    r = requests.post(
        GITHUB_GRAPHQL,
        headers=headers,
        json={"query": query, "variables": {"login": username}},
        timeout=15
    )

    if r.status_code != 200:
        print("[!] GraphQL error:", r.text)
        return []

    data = r.json()
    calendar = (
        data.get("data", {})
        .get("user", {})
        .get("contributionsCollection", {})
        .get("contributionCalendar", {})
    )

    signals = []
    collected_at = datetime.utcnow().isoformat() + "Z"

    total = calendar.get("totalContributions", 0)
    signals.append({
        "signal_type": "CONTRIBUTION_TOTAL",
        "value": str(total),
        "confidence": "HIGH",
        "source": "GitHub GraphQL",
        "collected_at": collected_at,
    })

    daily = []
    weekday = 0
    weekend = 0
    yearly = {}

    for week in calendar.get("weeks", []):
        for day in week.get("contributionDays", []):
            date = day["date"]
            count = day["contributionCount"]
            daily.append({"date": date, "count": count})

            dt = datetime.strptime(date, "%Y-%m-%d")
            year = str(dt.year)
            yearly[year] = yearly.get(year, 0) + count

            if dt.weekday() < 5:
                weekday += count
            else:
                weekend += count

    signals.append({
        "signal_type": "CONTRIBUTION_TIME_PATTERN",
        "value": f"Weekdays: {weekday}, Weekends: {weekend}",
        "confidence": "MEDIUM",
        "source": "GitHub GraphQL",
        "collected_at": collected_at,
    })

    for year, count in yearly.items():
        signals.append({
            "signal_type": "CONTRIBUTIONS_YEAR",
            "value": year,
            "confidence": "HIGH",
            "source": "GitHub GraphQL",
            "collected_at": collected_at,
            "meta": {"year": year, "count": count},
        })

    signals.append({
        "signal_type": "CONTRIBUTIONS_YEARLY_DATES",
        "value": daily,
        "confidence": "HIGH",
        "source": "GitHub GraphQL",
        "collected_at": collected_at,
    })

    return signals
