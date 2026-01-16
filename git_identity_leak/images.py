import os
import requests

def fetch_images_from_urls(urls, temp_dir):
    """
    Download images from given URLs into temp_dir.

    Args:
        urls (list): List of image URLs
        temp_dir (str): Directory to save images
    Returns:
        list: List of dicts with 'signal_type', 'value', and 'confidence'
    """
    os.makedirs(temp_dir, exist_ok=True)
    results = []

    for idx, url in enumerate(urls):
        try:
            ext = url.split("?")[0].split(".")[-1]  # try to infer extension
            if ext.lower() not in ["jpg", "jpeg", "png", "gif", "bmp", "webp"]:
                ext = "jpg"
            fname = os.path.join(temp_dir, f"image_{idx}.{ext}")
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(fname, "wb") as f:
                    f.write(r.content)
                results.append({"signal_type": "IMAGE_FILE", "value": fname, "confidence": "HIGH"})
        except Exception as e:
            print(f"[!] Image fetch failed: {e}")

    return results
