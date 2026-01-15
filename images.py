from PIL import Image
import os
import hashlib

def analyze_images(image_dir: str):
    signals = []
    for fname in os.listdir(image_dir):
        if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        path = os.path.join(image_dir, fname)
        img = Image.open(path)
        # Compute a simple hash for reuse detection
        h = hashlib.md5(img.tobytes()).hexdigest()
        signals.append({
            "type": "image",
            "value": fname,
            "hash": h,
            "confidence": 0.5,
            "signal_type": "INFERENCE",
            "evidence": "Image hash metadata"
        })
    return signals
