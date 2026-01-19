import os
import requests
from datetime import datetime
from collections import Counter
from bs4 import BeautifulSoup

def collect(username):
    signals = []
    collected_at = datetime.utcnow().isoformat() + "Z"

    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}

    # -----------------------------
    # Contribution calendar scrape
    # -----------------------------
    daily = []
    yearly = {}
    weekday_count = 0
    weekend_count = 0

    url = f"https://github.com/users/{username}/contributions"
    r = requests.get(url, headers=headers, timeout=15)

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        days = soup.find_all("rect", class_="ContributionCalendar-day")

        for d in days:
            date = d.get("data-date")
            count = int(d.get("data-count", 0))
            if not date:
                continue

            daily.append({"date": date, "count": count})

            dt = datetime.strptime(date, "%Y-%m-%d")
            year = str(dt.year)
            yearly[year] = yearly.get(year, 0) + count

            if dt.weekday() < 5:
                weekday_count += count
            else:
                weekend_count += count

    total = sum(y for y in yearly.values())

    # -----------------------------
    # Signals
    # -----------------------------
    signals.append({
        "signal_type": "CONTRIBUTION_TOTAL",
        "value": str(total),
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
            "meta": {"year": year, "count": count}
        })

    if daily:
        signals.append({
            "signal_type": "CONTRIBUTIONS_YEARLY_DATES",
            "value": daily,
            "confidence": "HIGH",
            "source": "GitHub contributions page",
            "collected_at": collected_at
        })

    return signals
