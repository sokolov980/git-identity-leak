# git_identity_leak/plugins/github.py
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from timezonefinder import TimezoneFinder
import pytz
from geopy.geocoders import Nominatim

ORCID_REGEX = r"(https?://orcid\.org/\d{4}-\d{4}-\d{4}-\d{4})"

SOCIAL_DOMAINS = {
    "twitter.com": "SOCIAL_TWITTER",
    "linkedin.com": "SOCIAL_LINKEDIN",
    "mastodon.social": "SOCIAL_MASTODON",
    "github.com": "SOCIAL_GITHUB",
}

PRONOUNS_REGEX = r"\b(?:he/him|she/her|they/them)\b"

def extract_social_links(text):
    links = []
    urls = re.findall(r"https?://[^\s]+", text)
    for url in urls:
        domain = urlparse(url).netloc.lower()
        key = SOCIAL_DOMAINS.get(domain)
        if key:
            links.append({"signal_type": key, "value": url})
        orcid_match = re.search(ORCID_REGEX, url)
        if orcid_match:
            links.append({"signal_type": "ORCID", "value": orcid_match.group(1)})
    return links

def detect_pronouns(text):
    match = re.search(PRONOUNS_REGEX, text.lower())
    return match.group(0) if match else None

def get_local_time(location_str):
    if not location_str:
        return None
    try:
        geolocator = Nominatim(user_agent="git_identity_leak")
        loc = geolocator.geocode(location_str, timeout=10)
        if not loc:
            return None
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lng=loc.longitude, lat=loc.latitude)
        if not tz_str:
            return None
        tz = pytz.timezone(tz_str)
        return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return None

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

        # --- Bio / blog ---
        for field in ["bio", "blog"]:
            if data.get(field):
                text = data[field]
                signals.append({"signal_type": field.upper(), "value": text, "confidence": "MEDIUM", "source": "GitHub", "collected_at": collected_at})
                for s in extract_social_links(text):
                    s.update({"confidence": "MEDIUM", "source": "GitHub", "collected_at": collected_at})
                    signals.append(s)
                # Detect pronouns in bio
                if field == "bio":
                    pronouns = detect_pronouns(text)
                    if pronouns:
                        signals.append({"signal_type": "PRONOUNS", "value": pronouns, "confidence": "MEDIUM", "source": "GitHub", "collected_at": collected_at})

        # --- Email, company, location ---
        for field in ["email", "company", "location"]:
            if data.get(field):
                signals.append({"signal_type": field.upper(), "value": data[field], "confidence": "MEDIUM", "source": "GitHub", "collected_at": collected_at})

        # --- Current local time if location provided ---
        if data.get("location"):
            local_time = get_local_time(data["location"])
            if local_time:
                signals.append({"signal_type": "LOCAL_TIME", "value": local_time, "confidence": "MEDIUM", "source": "GitHub", "collected_at": collected_at})

        # --- Twitter handle ---
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
