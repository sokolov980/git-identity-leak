import requests
from datetime import datetime

GITHUB_API = "https://api.github.com"

def fetch_commits(username: str):
    url = f"{GITHUB_API}/users/{username}/events/public"
    r = requests.get(url)
    if r.status_code != 200:
        return []
    events = r.json()
    commits = []
    for e in events:
        if e["type"] == "PushEvent":
            for commit in e["payload"]["commits"]:
                commits.append({
                    "author_name": commit["author"]["name"],
                    "author_email": commit["author"]["email"],
                    "message": commit["message"],
                    "timestamp": e["created_at"]
                })
    return commits
