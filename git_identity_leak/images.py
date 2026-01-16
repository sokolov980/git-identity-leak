# git_identity_leak/images.py
import os
import requests

def fetch_images_from_urls(urls, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    signals = []

    for idx, url in enumerate(urls):
        ext = url.split(".")[-1].split("?")[0]
        filename = os.path.join(output_dir, f"image_{idx}.{ext}")
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            with open(filename, "wb") as f:
                f.write(resp.content)
            signals.append({
                "signal_type": "IMAGE_FILE",
                "value": filename,
                "confidence": "HIGH"
            })
        except Exception as e:
            print(f"[!] Image fetch failed: {e}")

    return signals
