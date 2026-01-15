from git_identity_leak.plugins import load_plugins
from git_identity_leak.images import fetch_images_from_urls

def full_analysis(username, image_dir=None, include_stylometry=False, include_temporal=False):
    signals = []

    # Load plugins
    plugins = load_plugins(["github", "reddit", "x", "linkedin"])
    for plugin in plugins:
        plugin_signals = plugin.collect(username)
        signals.extend(plugin_signals)

    # Extract image URLs from plugin signals
    image_urls = [s["value"] for s in signals if s["signal_type"] == "IMAGE"]

    # Fetch remote images and analyze locally
    if image_dir and image_urls:
        image_signals = fetch_images_from_urls(image_urls, temp_dir=image_dir)
        signals.extend(image_signals)

    # Placeholder: Add temporal/stylometry analysis if requested
    temporal_data = {}
    stylometry_data = {}

    return signals, temporal_data, stylometry_data
