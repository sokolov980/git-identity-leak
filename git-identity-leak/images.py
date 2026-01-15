# git_identity_leak/images.py
import os
import requests
from urllib.parse import urljoin
from pathlib import Path

def fetch_image(url, save_dir):
    """
    Download a single image from a URL into save_dir.
    Returns the local path or None if failed.
    """
    try:
        filename = url.split("/")[-1]
        filepath = Path(save_dir) / filename
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return str(filepath)
    except requests.exceptions.RequestException:
        return None

def fetch_images_from_urls(urls, temp_dir="images"):
    """
    Fetch multiple images from a list of URLs.
    Returns a list of signal dicts for images successfully downloaded.
    """
    os.makedirs(temp_dir, exist_ok=True)
    signals = []

    for url in urls:
        local_path = fetch_image(url, temp_dir)
        if local_path:
            signals.append({
                "signal_type": "IMAGE",
                "value": local_path,
                "confidence": "HIGH"
            })
    return signals

def fetch_github_avatar(username, save_dir="images"):
    """
    Fetch GitHub profile avatar for the username.
    Returns signal dict if successful.
    """
    avatar_url = f"https://avatars.githubusercontent.com/{username}"
    local_path = fetch_image(avatar_url, save_dir)
    if local_path:
        return {
            "signal_type": "IMAGE",
            "value": local_path,
            "confidence": "HIGH"
        }
    return None

def fetch_repo_images(username, save_dir="images"):
    """
    Fetch images from public GitHub repos of the user.
    Scans README.md for image links ending with .png/.jpg/.jpeg/.gif
    Returns a list of signal dicts.
    """
    import requests
    import re

    signals = []
    headers = {"User-Agent": "git-identity-leak-osint/1.0"}
    repos_url = f"https://api.github.com/users/{username}/repos"

    try:
        resp = requests.get(repos_url, headers=headers, timeout=10)
        resp.raise_for_status()
        repos = resp.json()
        img_regex = re.compile(r'!\[.*?\]\((https?://[^\s)]+)\)')

        for repo in repos:
            readme_url = f"https://raw.githubusercontent.com/{username}/{repo['name']}/master/README.md"
            try:
                r = requests.get(readme_url, headers=headers, timeout=5)
                if r.status_code == 200:
                    matches = img_regex.findall(r.text)
                    for img_url in matches:
                        local_path = fetch_image(img_url, save_dir)
                        if local_path:
                            signals.append({
                                "signal_type": "REPO_README",
                                "value": local_path,
                                "confidence": "MEDIUM"
                            })
            except requests.exceptions.RequestException:
                continue
    except requests.exceptions.RequestException:
        pass

    return signals
