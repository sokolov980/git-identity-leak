# git_identity_leak/images.py
import os
import requests
from urllib.parse import urlparse

def sanitize_filename(url):
    """
    Convert URL into a safe filename.
    """
    parsed = urlparse(url)
    path = parsed.path.lstrip("/").replace("/", "_")
    if not path:
        path = "image"
    ext = path.split(".")[-1] if "." in path else "jpg"
    return f"{path}.{ext}"

def fetch_images_from_urls(urls, output_dir):
    """
    Fetch remote images and save them locally.

    Args:
        urls (list): List of image URLs.
        output_dir (str): Directory to save images.

    Returns:
        list of dict: IMAGE_FILE signals with local paths.
    """
    signals = []

    for idx, url in enumerate(urls):
        try:
            filename = sanitize_filename(url)
            full_path = os.path.join(output_dir, filename)

            # Make sure all parent directories exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Fetch the image
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            with open(full_path, "wb") as f:
                f.write(resp.content)

            signals.append({
                "signal_type": "IMAGE_FILE",
                "value": full_path,
                "confidence": "HIGH"
            })
        except Exception as e:
            print(f"[!] Image fetch failed: {e}")

    return signals
