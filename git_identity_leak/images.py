import os
import re
import requests


def fetch_images_from_urls(urls, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    results = []

    for idx, url in enumerate(urls):
        try:
            safe = re.sub(r"[^a-zA-Z0-9_.-]", "_", url)
            path = os.path.join(output_dir, f"image_{idx}.jpg")

            r = requests.get(url, timeout=10)
            r.raise_for_status()

            with open(path, "wb") as f:
                f.write(r.content)

            results.append({
                "signal_type": "IMAGE_LOCAL",
                "value": path,
                "confidence": "HIGH"
            })

        except Exception as e:
            print(f"[!] Image fetch failed: {e}")

    return results
