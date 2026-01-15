# git_identity_leak/analysis.py
import os
from datetime import datetime
from .plugins import load_plugins
from .images import fetch_images_from_urls, fetch_github_avatar, fetch_repo_images

def full_analysis(username, image_dir="images", include_stylometry=False, include_temporal=False):
    """
    Perform full OSINT analysis on a username.

    Args:
        username (str): Target username.
        image_dir (str): Directory to store downloaded images.
        include_stylometry (bool): Whether to include stylometry analysis.
        include_temporal (bool): Whether to include temporal analysis.

    Returns:
        signals (list): List of identity signals.
        temporal_data (dict): Temporal analysis results.
        stylometry_data (dict): Stylometry analysis results.
    """
    signals = []

    # -------------------
    # Load and run plugins
    # -------------------
    plugins = load_plugins(["github", "reddit", "x", "linkedin"])
    for plugin in plugins:
        try:
            plugin_signals = plugin.collect(username)
            # Ensure signals are dicts with required keys
            for s in plugin_signals:
                if isinstance(s, dict) and "signal_type" in s and "value" in s:
                    signals.append(s)
        except Exception as e:
            print(f"[!] Error running plugin {plugin.__name__}: {e}")

    # -------------------
    # Fetch images
    # -------------------
    image_signals = []

    # 1. GitHub avatar
    avatar_signal = fetch_github_avatar(username, save_dir=image_dir)
    if avatar_signal:
        image_signals.append(avatar_signal)

    # 2. Repo README images
    image_signals.extend(fetch_repo_images(username, save_dir=image_dir))

    # 3. Plugin-provided image URLs
    plugin_image_urls = [s["value"] for s in signals if s.get("signal_type") == "IMAGE" and s.get("value")]
    if plugin_image_urls:
        image_signals.extend(fetch_images_from_urls(plugin_image_urls, temp_dir=image_dir))

    # Add all image signals to main signals
    signals.extend(image_signals)

    # -------------------
    # Temporal analysis
    # -------------------
    temporal_data = {}
    if include_temporal:
        temporal_data = {
            "earliest_seen": datetime.utcnow().isoformat(),
            "latest_seen": datetime.utcnow().isoformat(),
            "duration_days": 0
        }

    # -------------------
    # Stylometry analysis
    # -------------------
    stylometry_data = {}
    if include_stylometry:
        stylometry_data = {
            "top_words": [],
            "note": "Experimental; do not rely solely on this for identity."
        }

    return signals, temporal_data, stylometry_data
