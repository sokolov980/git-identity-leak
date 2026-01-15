# git-identity-leak/analysis.py

from plugins import load_plugins
from images import fetch_images_from_urls
from datetime import datetime

def normalize_signal(signal, signal_type):
    """
    Ensure all signals have the same dict structure.
    """
    value = signal.get("value") or signal.get("username") or signal.get("email") or signal.get("image")
    confidence = signal.get("confidence", 0.5)
    return {"signal_type": signal_type, "value": value, "confidence": confidence}

def full_analysis(username, image_dir=None, include_stylometry=False, include_temporal=False):
    """
    Perform full OSINT analysis on a username.

    Returns:
        signals (list of dict)
        temporal_data (dict)
        stylometry_data (dict)
    """
    signals = []

    # Load all plugins
    plugins = load_plugins(["github", "reddit", "x", "linkedin"])
    for plugin in plugins:
        try:
            plugin_signals = plugin.collect(username)
            for sig in plugin_signals:
                signals.append(normalize_signal(sig, sig.get("signal_type", "unknown")))
        except Exception as e:
            plugin_name = getattr(plugin, "__name__", "unknown")
            print(f"[!] Error running plugin {plugin_name}: {e}")

    # Fetch images from signals
    image_urls = [s["value"] for s in signals if s["signal_type"] == "image" and s.get("value")]
    if image_dir and image_urls:
        image_signals = fetch_images_from_urls(image_urls, temp_dir=image_dir)
        signals.extend(image_signals)

    # Temporal analysis placeholder
    temporal_data = {}
    if include_temporal:
        temporal_data = {
            "earliest_seen": datetime.utcnow().isoformat(),
            "latest_seen": datetime.utcnow().isoformat(),
            "duration_days": 0
        }

    # Stylometry analysis placeholder
    stylometry_data = {}
    if include_stylometry:
        stylometry_data = {
            "top_words": [],
            "note": "Experimental; do not rely solely on this for identity."
        }

    return signals, temporal_data, stylometry_data
