from datetime import datetime
from git_identity_leak.plugins import load_plugins
from git_identity_leak.images import fetch_images_from_urls


def full_analysis(username, image_dir=None, include_temporal=False, include_stylometry=False):
    signals = []

    plugins = load_plugins(["github", "reddit", "x", "linkedin"])
    for plugin in plugins:
        try:
            signals.extend(plugin.collect(username))
        except Exception as e:
            signals.append({
                "signal_type": "PLUGIN_ERROR",
                "value": f"{plugin.__name__}: {e}",
                "confidence": "LOW"
            })

    image_urls = [
        s["value"] for s in signals
        if s["signal_type"] == "IMAGE"
    ]

    if image_dir and image_urls:
        signals.extend(fetch_images_from_urls(image_urls, image_dir))

    temporal_data = {}
    stylometry_data = {}

    if include_temporal:
        now = datetime.utcnow().isoformat()
        temporal_data = {
            "earliest_seen": now,
            "latest_seen": now,
            "duration_days": 0
        }

    if include_stylometry:
        stylometry_data = {
            "top_words": [],
            "note": "Experimental; do not rely solely on this for identity."
        }

    return signals, temporal_data, stylometry_data
