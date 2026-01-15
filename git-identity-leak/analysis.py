# analysis.py

from plugins import load_plugins
from images import fetch_images_from_urls
from reuse import check_username_reuse, check_email_reuse
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

    # 1️⃣ Load and run plugins
    plugins = load_plugins(["github", "reddit", "x", "linkedin"])
    for plugin in plugins:
        try:
            plugin_signals = plugin.collect(username)
            signals.extend(plugin_signals)
        except Exception as e:
            print(f"[!] Error running plugin {plugin.__name__}: {e}")

    # 2️⃣ Fetch images from IMAGE signals
    image_urls = [s["value"] for s in signals if s.get("signal_type") == "IMAGE"]
    if image_dir and image_urls:
        image_signals = fetch_images_from_urls(image_urls, temp_dir=image_dir)
        signals.extend(image_signals)

    # 3️⃣ Check username/email reuse across platforms
    username_reuse_signals = check_username_reuse(username)
    signals.extend([{"signal_type": "USERNAME_REUSE", **r} for r in username_reuse_signals])

    # Example: GitHub noreply email format
    email_to_check = f"{username}+123456@users.noreply.github.com"
    email_reuse_signals = check_email_reuse(email_to_check)
    signals.extend([{"signal_type": "EMAIL_REUSE", **r} for r in email_reuse_signals])

    # 4️⃣ Placeholder for temporal & stylometry analysis
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


# --- Individual functions for self_audit CLI
def analyze_username(username):
    return [{"signal_type": "USERNAME", "value": username, "confidence": 0.9, "source": "self_audit"}]

def analyze_email(username):
    email = f"{username}+123456@users.noreply.github.com"
    return [{"signal_type": "EMAIL", "value": email, "confidence": 0.7, "source": "self_audit"}]

def analyze_posts(username):
    # Placeholder: could be replaced with plugin post scraping
    return [{"signal_type": "POST", "value": "", "confidence": 0.1, "source": "self_audit"}]
