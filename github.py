import requests

GITHUB_API = "https://api.github.com"

def fetch_repos(username):
    url = f"{GITHUB_API}/users/{username}/repos"
    r = requests.get(url)
    if r.status_code != 200:
        return []
    return r.json()

def fetch_commit_metadata(username, max_commits=50):
    repos = fetch_repos(username)
    commits_data = []

    for repo in repos:
        if repo.get("fork"):
            continue

        commits_url = f"{GITHUB_API}/repos/{username}/{repo['name']}/commits"
        r = requests.get(commits_url)
        if r.status_code != 200:
            continue

        for commit in r.json()[:max_commits]:
            commit_info = commit.get("commit", {})
            author = commit_info.get("author", {})

            commits_data.append({
                "repo": repo["name"],
                "author_name": author.get("name"),
                "author_email": author.get("email"),
                "timestamp": author.get("date")
            })

    return commits_data
