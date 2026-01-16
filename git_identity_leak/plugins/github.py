# git_identity_leak/plugins/github.py
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re  # For regex matching ORCID and social links
from urllib.parse import urlparse

ORCID_REGEX = r"(https?://orcid\.org/\d{4}-\d{4}-\d{4}-\d{4})"

SOCIAL_DOMAINS = {
    "twitter.com": "SOCIAL_TWITTER",
    "linkedin.com": "SOCIAL_LINKEDIN",
    "mastodon.social": "SOCIAL_MASTODON",
    "github.com": "SOCIAL_GITHUB",
}

def extract_social_links(text):
    """
    Extract social URLs from text and categorize by domain.
    Returns list of dicts: {signal_type, value}
    """
    links = []
    urls = re.findall(r"https?://[^\s]+", text)
    for url in urls:
        domain = urlparse(url).netloc.lower()
        key = SOCIAL_DOMAINS.get(domain)
        if key:
            links.append({"signal_type": key, "value": url})
        # ORCID detection
        orcid_match = re.search(ORCID_REGEX, url)
        if orcid_match:
            links.append({"signal_type": "ORCID", "value": orcid_match.group(1)})
    return links

def collect(username):
    signals = []
    collected_at = datetime.utcnow().isoformat() + "Z"

    user_url = f"https://api.github.com/users/{username}"
    try:
        r = requests.get(user_url, timeout=10)
        if r.status_code != 200:
            return signals
        data = r.json()

        # --- Basic info ---
        if data.get("name"):
            signals.append({"signal_type": "NAME", "value": data["name"], "confidence": "HIGH", "source": "GitHub", "collected_at": collected_at})

        signals.append({"signal_type": "USERNAME", "value": username, "confidence": "HIGH", "source": "GitHub", "collected_at": collected_at})

        if data.get("avatar_url"):
            signals.append({"signal_type": "IMAGE", "value": data["avatar_url"], "confidence": "HIGH", "source": "GitHub", "collected_at": collected_at})

        # Fields to extract and parse for social links
        for field in ["bio", "blog"]:
            if data.get(field):
                text = data[field]
                signals.append({"signal_type": field.upper(), "value": text, "confidence": "MEDIUM", "source": "GitHub", "collected_at": collected_at})
                social_signals = extract_social_links(text)
                for s in social_signals:
                    s.update({"confidence": "MEDIUM", "source": "GitHub", "collected_at": collected_at})
                    signals.append(s)

        # Email, company, location, pronouns
        for field in ["email", "company", "location"]:
            if data.get(field):
                signals.append({"signal_type": field.upper(), "value": data[field], "confidence": "MEDIUM", "source": "GitHub", "collected_at": collected_at})

        # Twitter username as social
        if data.get("twitter_username"):
            signals.append({"signal_type": "SOCIAL_TWITTER", "value": f"https://twitter.com/{data['twitter_username']}", "confidence": "MEDIUM", "source": "GitHub", "collected_at": collected_at})

        # --- Profile README ---
        profile_readme_url = f"https://raw.githubusercontent.com/{username}/{username}/master/README.md"
        try:
            resp = requests.head(profile_readme_url, timeout=5)
            if resp.status_code == 200:
                signals.append({"signal_type": "PROFILE_README", "value": profile_readme_url, "confidence": "MEDIUM", "source": "GitHub", "collected_at": collected_at})
        except Exception:
            pass

        # --- Contributions per year ---
        contrib_url = f"https://github.com/users/{username}/contributions"
        try:
            r = requests.get(contrib_url, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                years = {}
                for rect in soup.find_all("rect", {"class": "ContributionCalendar-day"}):
                    date = rect.get("data-date")
                    count = int(rect.get("data-count", "0"))
                    if date:
                        year = date.split("-")[0]
                        years[year] = years.get(year, 0) + count
                for year, total in sorted(years.items(), reverse=True):
                    signals.append({"signal_type": "CONTRIBUTIONS", "value": f"{year}: {total}", "confidence": "MEDIUM", "source": "GitHub", "collected_at": collected_at})
        except Exception:
            pass

        # --- Repositories ---
        repos_url = data.get("repos_url")
        if repos_url:
            repos = requests.get(repos_url, timeout=10).json()
            for repo in repos:
                repo_name = repo.get("name", "unknown")
                stars = repo.get("stargazers_count", 0)
                description = repo.get("description") or ""
                language = repo.get("language") or ""
                updated_at = repo.get("updated_at", "unknown").split("T")[0]
                readme_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/master/README.md"
                summary = f"{repo_name} | Stars: {stars} | {description} | Lang: {language} | Last Updated: {updated_at} | README: {readme_url}"
                signals.append({"signal_type": "REPO_SUMMARY", "value": summary, "confidence": "HIGH", "source": "GitHub", "collected_at": collected_at})

        # --- Achievements / badges ---
        achievements_url = f"https://github.com/{username}?tab=achievements"
        try:
            r = requests.get(achievements_url, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                badges = [b.get("alt") for b in soup.find_all("img", {"class": "achievement-badge"}) if b.get("alt")]
                for badge in badges:
                    signals.append({"signal_type": "BADGE", "value": badge, "confidence": "MEDIUM", "source": "GitHub", "collected_at": collected_at})
        except Exception:
            pass

    except Exception as e:
        print(f"[!] GitHub plugin error for user {username}: {e}")

    return signals
