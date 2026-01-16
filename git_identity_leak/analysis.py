# git_identity_leak/analysis.py
import datetime
from .plugins import load_plugins
from .images import fetch_images_from_urls

def full_analysis(username, image_dir=None, include_temporal=False, include_stylometry=False):
    """
    Perform full OSINT analysis on a username.

    Args:
        username (str): Target username.
        image_dir (str, optional): Directory to store downloaded images.
        include_temporal (bool): Whether to include temporal analysis.
        include_stylometry (bool): Whether to include stylometry analysis.

    Returns:
        signals (list[dict]): List of signals found.
        temporal_data (dict): Temporal analysis results.
        stylometry_data (dict): Stylometry analysis results.
    """
    signals = []

    # Load all available plugins
    plugins = load_plugins(["github", "reddit", "x", "linkedin"])
    for plugin in plugins:
        try:
            plugin_signals = plugin.collect(username)
            if plugin_signals:
                signals.extend(plugin_signals)
        except Exception as e:
            print(f"[!] Error collecting from plugin {plugin.__name__}: {e}")

    # Extract IMAGE URLs for fetching
    image_urls = [s["value"] for s in signals if s.get("signal_type") == "IMAGE"]

    # Fetch images and save locally
    if image_dir and image_urls:
        try:
            image_signals = fetch_images_from_urls(image_urls, image_dir)
            signals.extend(image_signals)
        except Exception as e:
            print(f"[!] Error fetching images: {e}")

    # Temporal analysis (placeholder)
    temporal_data = {}
    if include_temporal:
        now = datetime.datetime.utcnow().isoformat()
        temporal_data = {
            "earliest_seen": now,
            "latest_seen": now,
            "duration_days": 0
        }

    # Stylometry analysis (placeholder)
    stylometry_data = {}
    if include_stylometry:
        stylometry_data = {
            "top_words": [],
            "note": "Experimental; do not rely solely on this for identity."
        }

    return signals, temporal_data, stylometry_data
