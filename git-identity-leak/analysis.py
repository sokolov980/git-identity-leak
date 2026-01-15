# analysis.py

from plugins import load_plugins
from images import fetch_images_from_urls
from datetime import datetime

def full_analysis(username, image_dir=None, include_stylometry=False, include_temporal=False):
    """
    Perform full OSINT analysis on a username.

    Returns:
        signals (list), temporal_data (dict), stylometry_data (dict)
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

    # Fetch images
    if image_dir and image_urls:
        image_signals = fetch_images_from_urls(image_urls, temp_dir=image_dir)
        signals.extend(image_signals)

    # Placeholder temporal and stylometry data
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


# --- Add separate analysis functions for self_audit ---
def analyze_username(username):
    # Example: just return username signal
    return [{"signal_type": "USERNAME", "value": username, "confidence": 0.9, "source": "self_audit"}]

def analyze_email(username):
    # Example: detect GitHub noreply email pattern
    return [{"signal_type": "EMAIL", "value": f"{username}+123456@users.noreply.github.com",
             "confidence": 0.7, "source": "self_audit"}]

def analyze_posts(username):
    # Example placeholder: returns empty post list
    return [{"signal_type": "POST", "value": "", "confidence": 0.1, "source": "self_audit"}]
