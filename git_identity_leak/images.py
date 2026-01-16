# git_identity_leak/images.py
import os
import requests

def fetch_images_from_urls(urls, output_dir):
    """
    Download images from given URLs into output_dir. Creates folders as needed.
    Returns a list of signal dicts.
    """
    os.makedirs(output_dir, exist_ok=True)
    signals = []

    for idx, url in enumerate(urls):
        # Get a file extension from the URL (fallback to jpg)
        ext = url.split(".")[-1].split("?")[0]
        if ext.lower() not in ["jpg", "jpeg", "png", "gif"]:
            ext = "jpg"
        filename = os.path.join(output_dir, f"image_{idx}.{ext}")

        # Ensure directory exists
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
