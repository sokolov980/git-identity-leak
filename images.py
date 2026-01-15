# git_identity_leak/images.py
import os
import requests
from PIL import Image
from datetime import datetime

def analyze_images(image_dir):
    results = []

    if not os.path.isdir(image_dir):
        print(f"[!] Image directory '{image_dir}' not found. Skipping image analysis.")
        return results

    for fname in os.listdir(image_dir):
        path = os.path.join(image_dir, fname)
        if not os.path.isfile(path):
            continue

        metadata = {}
        try:
            with Image.open(path) as img:
                metadata["format"] = img.format
                metadata["mode"] = img.mode
                metadata["size"] = img.size
        except Exception as e:
            print(f"[!] Failed to read image '{fname}': {e}")

        results.append({
            "value": fname,
            "confidence": 0.5,
            "signal_type": "INFERENCE",
            "evidence": f"File exists: {fname}, metadata: {metadata}",
            "first_seen": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat()
        })

    return results

def fetch_images_from_urls(urls, temp_dir="images"):
    os.makedirs(temp_dir, exist_ok=True)
    results = []

    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                filename = os.path.join(temp_dir, url.split("/")[-1])
                with open(filename, "wb") as f:
                    f.write(resp.content)
                img = Image.open(filename)
                results.append({
                    "value": filename,
                    "confidence": 0.9,
                    "signal_type": "IMAGE",
                    "evidence": url,
                    "first_seen": datetime.utcnow().isoformat(),
                    "last_seen": datetime.utcnow().isoformat()
                })
        except Exception as e:
            print(f"[!] Failed to fetch image {url}: {e}")

    return results
