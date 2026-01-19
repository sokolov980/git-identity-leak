import os
import requests
from datetime import datetime
from collections import Counter
from bs4 import BeautifulSoup

GITHUB_UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) GitIdentityLeak/1.0"
}

def collect(username):
    signals = []
    collected_at = datetime.utcnow().isoformat() + "Z"

    token = os.environ.get("GITHUB_TOKEN")
    headers = GITHUB_UA.copy()
    if token:
        headers["Authorization"] = f"token {token}"

    # ---------------- BASIC PROFILE ----------------
    r = requests.get(f"https://api.github.com/users/{username}", headers=headers)
    if r.status_code != 200:
        return signals

    data = r.json()

    signals.append({"signal_type":"USERNAME","value":data["login"],"confidence":"HIGH"})
    signals.append({"signal_type":"IMAGE","value":data["avatar_url"],"confidence":"HIGH"})
    signals.append({"signal_type":"FOLLOWERS","value":str(data["followers"]),"confidence":"HIGH"})
    signals.append({"signal_type":"FOLLOWING","value":str(data["following"]),"confidence":"HIGH"})
    signals.append({"signal_type":"PUBLIC_REPOS","value":str(data["public_repos"]),"confidence":"HIGH"})

    # ---------------- CONTRIBUTIONS (SVG SCRAPE) ----------------
    contrib_url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(contrib_url, headers=headers)

    daily = []
    yearly = {}
    weekday = weekend = 0

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")
        rects = soup.find_all("rect", {"data-date": True})

        for r in rects:
            date = r["data-date"]
            count = int(r.get("data-count", 0))
            dt = datetime.strptime(date, "%Y-%m-%d")

            daily.append({"date": date, "count": count})
            yearly[dt.year] = yearly.get(dt.year, 0) + count

            if dt.weekday() < 5:
                weekday += count
            else:
                weekend += count

    total = sum(yearly.values())

    signals.append({
        "signal_type": "CONTRIBUTION_TOTAL",
        "value": str(total),
        "confidence": "HIGH"
    })

    signals.append({
        "signal_type": "CONTRIBUTION_TIME_PATTERN",
        "value": f"Weekdays: {weekday}, Weekends: {weekend}",
        "confidence": "MEDIUM"
    })

    for y, c in sorted(yearly.items()):
        signals.append({
            "signal_type": "CONTRIBUTIONS_YEAR",
            "value": str(y),
            "confidence": "HIGH",
            "meta": {"year": y, "count": c}
        })

    if daily:
        signals.append({
            "signal_type": "CONTRIBUTIONS_YEARLY_DATES",
            "value": daily,
            "confidence": "HIGH"
        })

    return signals
