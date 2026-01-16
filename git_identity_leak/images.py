# git_identity_leak/images.py
import os
import requests
from urllib.parse import urlparse
from datetime import datetime
import hashlib

def sanitize_filename(url):
    parsed = urlparse(url)
    path = parsed.path.lstrip("/").replace("/", "_")
    if not path:
        path = "image"
    ext = path.split(".")[-1] if "." in path else "jpg"
    return f"{path}.{ext}"

def fetch_images_from_urls(urls, output_dir):
    signals = []

    for url in urls:
        try:
            filename = sanitize_filename(url)
            full_path = os.path.join(output_dir, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            with open(full_path, "wb") as f:
                f.write(resp.content)

            # Optional: compute SHA1 hash for deduplication
            hash_val = hashlib.sha1(resp.content).hexdigest()

            signals.append({
                "signal_type": "IMAGE_FILE",
                "value": full_path,
                "confidence": "HIGH",
                "source": "Image",
                "collected_at": datetime.utcnow().isoformat() + "Z",
                "hash": hash_val
            })

        except Exception as e:
            print(f"[!] Image fetch failed: {e}")

    return signals
