# git_identity_leak/images.py
import os
import requests

def fetch_images_from_urls(urls, output_dir):
    """
    Fetch images from a list of URLs and save them to output_dir.
    Returns a list of signals in standard format.
    """
    signals = []

    if not urls:
        return signals

    os.makedirs(output_dir, exist_ok=True)

    for idx, url in enumerate(urls):
        # Clean URL for filename
        safe_url = url.replace("://", "/").replace("/", "_").replace("?", "_").replace("&", "_")
        ext = url.split(".")[-1].split("?")[0]
        if len(ext) > 5 or not ext.isalnum():
            ext = "jpg"  # fallback extension
        filename = os.path.join(output_dir, f"image_{idx}.{ext}")

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

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
