from PIL import Image
from PIL.ExifTags import TAGS
import os

def analyze_images(folder):
    results = []
    if not folder or not os.path.isdir(folder):
        return results

    for filename in os.listdir(folder):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        path = os.path.join(folder, filename)
        exif_data = {}
        confidence = "LOW"
        try:
            with Image.open(path) as img:
                info = img._getexif()
                if info:
                    for tag, value in info.items():
                        decoded = TAGS.get(tag, tag)
                        exif_data[decoded] = value
                    confidence = "MEDIUM" if exif_data else "LOW"
        except Exception:
            pass
        results.append({"filename": filename, "exif": exif_data, "confidence": confidence})
    return results
