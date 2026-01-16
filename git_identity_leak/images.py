import os
import requests


def fetch_images_from_urls(urls, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    results = []

    for idx, url in enumerate(urls):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                ext = url.split("?")[0].split(".")[-1]
                path = os.path.join(output_dir, f"image_{idx}.{ext}")
                with open(path, "wb") as f:
                    f.write(r.content)

                results.append({
                    "signal_type": "IMAGE_FILE",
                    "value": path,
                    "confidence": "HIGH",
                })
        except Exception as e:
            print(f"[!] Image fetch failed: {e}")

    return results
