# analysis.py

from plugins import load_plugins
from images import fetch_images_from_urls
from datetime import datetime

def full_analysis(username, image_dir=None, include_stylometry=False, include_temporal=False):
    """
    Perform full OSINT analysis on a username.

    Args:
        username (str): Target username.
        image_dir (str, optional): Directory to store images.
        include_stylometry (bool): Include stylometry analysis if True.
        include_temporal (bool): Include temporal analysis if True.

    Returns:
        signals (list): List of identity signals.
        temporal_data (dict): Temporal analysis results.
        stylometry_data (dict): Stylometry analysis results.
    """
    signals = []

    # Load plugins
    plugins = load_plugins(["github", "reddit", "x", "linkedin"])
    for plugin in plugins:
        try:
            plugin_signals = plugin.collect(username)
            signals.extend(plugin_signals)
        except Exception as e:
            print(f"[!] Error running plugin {plugin.__name__}: {e}")

    # Extract image URLs from plugin signals
    image_urls = [s["value"] for s in signals if s.get("signal_type") == "IMAGE"]

    # Fetch remote images and analyze locally
    if image_dir and image_urls:
        image_signals = fetch_images_from_urls(image_urls, temp_dir=image_dir)
        signals.extend(image_signals)

    # Placeholder for temporal and stylometry analysis
    temporal_data = {}
    stylometry_data = {}

    if include_temporal:
        temporal_data = {
            "earliest_seen": datetime.utcnow().isoformat(),
            "latest_seen": datetime.utcnow().isoformat(),
            "duration_days": 0
        }

    if include_stylometry:
        stylometry_data = {
            "top_words": [],
            "note": "Experimental; do not rely solely on this for identity."
        }

    return signals, temporal_data, stylometry_data
