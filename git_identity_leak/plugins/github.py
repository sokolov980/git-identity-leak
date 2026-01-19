import os
import requests
from datetime import datetime

GQL_ENDPOINT = "https://api.github.com/graphql"

def collect(username):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return []

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
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
                weekday
              }
            }
          }
        }
      }
    }
    """

    resp = requests.post(
        GQL_ENDPOINT,
        headers=headers,
        json={"query": query, "variables": {"login": username}},
        timeout=15
    )

    if resp.status_code != 200:
        return []

    data = resp.json()
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]

    signals = []
    daily = []
    yearly = {}
    weekday = weekend = 0

    for week in cal["weeks"]:
        for d in week["contributionDays"]:
            date = d["date"]
            count = d["contributionCount"]
            dt = datetime.strptime(date, "%Y-%m-%d")

            daily.append({"date": date, "count": count})
            yearly[dt.year] = yearly.get(dt.year, 0) + count

            if dt.weekday() < 5:
                weekday += count
            else:
                weekend += count

    signals.append({
        "signal_type": "CONTRIBUTION_TOTAL",
        "value": str(cal["totalContributions"]),
        "confidence": "HIGH"
    })

    signals.append({
        "signal_type": "CONTRIBUTION_TIME_PATTERN",
        "value": f"Weekdays: {weekday}, Weekends: {weekend}",
        "confidence": "MEDIUM"
    })

    for year, count in sorted(yearly.items()):
        signals.append({
            "signal_type": "CONTRIBUTIONS_YEAR",
            "value": str(year),
            "confidence": "HIGH",
            "meta": {"year": year, "count": count}
        })

    signals.append({
        "signal_type": "CONTRIBUTIONS_YEARLY_DATES",
        "value": daily,
        "confidence": "HIGH"
    })

    return signals
