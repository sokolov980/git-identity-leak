import os
import requests

def fetch_images_from_urls(urls, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    signals = []
    for i, url in enumerate(urls):
        try:
            ext = url.split(".")[-1].split("?")[0]
            filename = os.path.join(output_dir, f"image_{i}.{ext}")
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            with open(filename, "wb") as f:
                f.write(r.content)
            signals.append({"signal_type": "LOCAL_IMAGE", "value": filename, "confidence": "HIGH"})
        except Exception as e:
            print(f"[!] Image fetch failed: {e}")
    return signals
