# git_identity_leak/images.py
import os
import requests

def fetch_images_from_urls(urls, temp_dir="./images"):
    """
    Download images from given URLs into temp_dir.
    """
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    signals = []
    for url in urls:
        try:
            filename = os.path.join(temp_dir, os.path.basename(url))
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            with open(filename, "wb") as f:
                f.write(r.content)
            signals.append({
                "signal_type": "IMAGE_FILE",
                "value": filename,
                "confidence": "HIGH"
            })
        except Exception as e:
            print(f"[!] Failed to fetch image {url}: {e}")
    return signals
