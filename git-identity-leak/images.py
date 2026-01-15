# git-identity-leak/images.py

import os
import requests
from PIL import Image
from io import BytesIO

def fetch_images_from_urls(urls, temp_dir="./images"):
    """
    Download images from URLs and save locally.
    Returns list of dict signals.
    """
    os.makedirs(temp_dir, exist_ok=True)
    signals = []

    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content))
            filename = os.path.join(temp_dir, os.path.basename(url))
            img.save(filename)
            signals.append({"signal_type": "image", "value": filename, "confidence": 1.0})
        except Exception as e:
            print(f"[!] Failed to fetch image {url}: {e}")

    return signals
