# images.py

import os
import requests

def fetch_images_from_urls(url_list, temp_dir="images"):
    """
    Download images from URLs into a directory and return as signals
    """
    os.makedirs(temp_dir, exist_ok=True)
    signals = []

    for url in url_list:
        try:
            filename = os.path.join(temp_dir, os.path.basename(url))
            resp = requests.get(url, stream=True)
            if resp.status_code == 200:
                with open(filename, "wb") as f:
                    for chunk in resp.iter_content(1024):
                        f.write(chunk)
                signals.append({"signal_type": "IMAGE", "value": filename, "confidence": "HIGH", "source": "images.py"})
        except Exception as e:
            print(f"[!] Failed to fetch image {url}: {e}")

    return signals
