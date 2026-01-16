import os
import requests

def fetch_images_from_urls(urls, temp_dir="./images"):
    os.makedirs(temp_dir, exist_ok=True)
    results = []
    for i, url in enumerate(urls):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                ext = url.split(".")[-1].split("?")[0]
                filename = f"{temp_dir}/img_{i}.{ext}"
                with open(filename, "wb") as f:
                    f.write(r.content)
                results.append({"signal_type": "IMAGE_FILE", "value": filename, "confidence": "HIGH"})
        except Exception as e:
            print(f"[!] Error fetching image {url}: {e}")
    return results
