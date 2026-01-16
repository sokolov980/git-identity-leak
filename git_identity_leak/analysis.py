from plugins import load_plugins
from images import fetch_images_from_urls
from datetime import datetime

def full_analysis(username, image_dir=None, include_stylometry=False, include_temporal=False):
    signals = []

    # Load all plugins
    plugins = load_plugins()
    for plugin in plugins:
        try:
            plugin_signals = plugin.collect(username)
            signals.extend(plugin_signals)
        except Exception as e:
            print(f"[!] Error running plugin {plugin.__name__}: {e}")

    # Extract image URLs
    image_urls = [s["value"] for s in signals if s["signal_type"] == "IMAGE"]

    # Fetch images locally
    if image_dir and image_urls:
        image_signals = fetch_images_from_urls(image_urls, image_dir)
        signals.extend(image_signals)

    # Temporal data
    temporal_data = {}
    if include_temporal:
        now = datetime.utcnow().isoformat()
        temporal_data = {"earliest_seen": now, "latest_seen": now, "duration_days": 0}

    # Stylometry
    stylometry_data = {}
    if include_stylometry:
        stylometry_data = {"top_words": [], "note": "Experimental; do not rely solely on this for identity."}

    return signals, temporal_data, stylometry_data
