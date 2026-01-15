import os
from PIL import Image  # make sure Pillow is installed
from datetime import datetime

def analyze_images(image_dir):
    """
    Analyze images in the given directory for metadata, faces, etc.
    Returns a list of signals for each image.
    """
    results = []

    if not os.path.isdir(image_dir):
        print(f"[!] Image directory '{image_dir}' not found. Skipping image analysis.")
        return results

    for fname in os.listdir(image_dir):
        path = os.path.join(image_dir, fname)
        if not os.path.isfile(path):
            continue  # skip subdirectories

        # Placeholder: Basic metadata extraction
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
            "confidence": 0.5,  # placeholder confidence
            "signal_type": "INFERENCE",
            "evidence": f"File exists: {fname}, metadata: {metadata}",
            "first_seen": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat()
        })

    return results
