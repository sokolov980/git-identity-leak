import requests
import time

GITHUB_API = "https://api.github.com"

def fetch_repos(username):
    url = f"{GITHUB_API}/users/{username}/repos"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return []

def fetch_commit_metadata(username, max_commits=50):
    repos = fetch_repos(username)
    commits_data = []

    for repo in repos:
        if repo.get("fork"):
            continue
        commits_url = f"{GITHUB_API}/repos/{username}/{repo['name']}/commits"
        try:
            r = requests.get(commits_url, timeout=10)
            r.raise_for_status()
            for commit in r.json()[:max_commits]:
                c = commit.get("commit", {}).get("author", {})
                commits_data.append({
                    "repo": repo["name"],
                    "author_name": c.get("name"),
                    "author_email": c.get("email"),
                    "timestamp": c.get("date")
                })
            time.sleep(0.5)  # simple rate-limit mitigation
        except requests.RequestException:
            continue

    return commits_data
