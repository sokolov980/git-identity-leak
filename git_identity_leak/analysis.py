# git_identity_leak/analysis.py

from .plugins import load_plugins
from .images import fetch_images_from_urls
from datetime import datetime

def full_analysis(username, image_dir=None, include_stylometry=False, include_temporal=False,
                  check_username=False, check_email=False, check_posts=False):
    """
    Perform full OSINT analysis on a username.

    Args:
        username (str): Target username.
        image_dir (str, optional): Directory to store images.
        include_stylometry (bool): Include stylometry analysis if True.
        include_temporal (bool): Include temporal analysis if True.
        check_username (bool): Check username reuse across platforms
        check_email (bool): Check email reuse across platforms
        check_posts (bool): Check public posts across platforms

    Returns:
        signals (list): List of identity signals.
        temporal_data (dict): Temporal analysis results.
        stylometry_data (dict): Stylometry analysis results.
    """
    signals = []

    # Load all plugins
    plugins = load_plugins(["github", "reddit", "x", "linkedin"])
    for plugin in plugins:
        try:
            plugin_signals = plugin.collect(username)
            signals.extend(plugin_signals)
        except Exception as e:
            print(f"[!] Error running plugin {plugin.__name__}: {e}")

    # Filter signals based on flags
    filtered_signals = []
    for s in signals:
        signal_type = s.get("signal_type", "")
        if ((check_username and signal_type == "USERNAME") or
            (check_email and signal_type == "EMAIL") or
            (check_posts and signal_type in ["POST_PLATFORM", "REPO_README", "PROFILE_PLATFORM"]) or
            (signal_type not in ["USERNAME", "EMAIL", "POST_PLATFORM", "REPO_README", "PROFILE_PLATFORM"])):
            filtered_signals.append(s)

    # Fetch images from URLs if requested
    image_urls = [s["value"] for s in filtered_signals if s.get("signal_type") == "IMAGE"]
    if image_dir and image_urls:
        image_signals = fetch_images_from_urls(image_urls, temp_dir=image_dir)
        filtered_signals.extend(image_signals)

    # Temporal analysis
    temporal_data = {}
    if include_temporal:
        temporal_data = {
            "earliest_seen": datetime.utcnow().isoformat(),
            "latest_seen": datetime.utcnow().isoformat(),
            "duration_days": 0
        }

    # Stylometry analysis
    stylometry_data = {}
    if include_stylometry:
        stylometry_data = {
            "top_words": [],
            "note": "Experimental; do not rely solely on this for identity."
        }

    return filtered_signals, temporal_data, stylometry_data
