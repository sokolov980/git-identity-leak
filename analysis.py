from schemas import Signal
from github_api import fetch_commits
from reuse import check_username_reuse, check_email_reuse
from images import analyze_images
from posts import analyze_posts as fetch_posts  # FIXED: renamed to avoid recursion
from inference import apply_inference
from temporal import analyze_temporal
from stylometry import analyze_stylometry
from plugins import load_plugins
from typing import List

def analyze_username(username: str) -> List[Signal]:
    signals = []

    # GitHub + other platform username reuse
    reuse_results = check_username_reuse(username)
    for r in reuse_results:
        signals.append(Signal(
            type="username",
            value=username,
            confidence=r["confidence"],
            signal_type="FACT" if r["found"] else "INFERENCE",
            evidence=r.get("evidence"),
            first_seen=r.get("first_seen"),
            last_seen=r.get("last_seen")
        ))

    # Plugin-based additional username collection
    plugins = load_plugins(["reddit", "x", "linkedin"])  # will warn if missing
    for plugin in plugins:
        try:
            plugin_signals = plugin.collect(username)
            for s in plugin_signals:
                signals.append(Signal(**s))
        except Exception as e:
            print(f"[!] Plugin error: {e}")

    return signals

def analyze_email(username: str) -> List[Signal]:
    signals = []

    email_results = check_email_reuse(username)
    for r in email_results:
        signals.append(Signal(
            type="email",
            value=r["value"],
            confidence=r["confidence"],
            signal_type="FACT" if r["found"] else "INFERENCE",
            evidence=r.get("evidence"),
            first_seen=r.get("first_seen"),
            last_seen=r.get("last_seen")
        ))

    return signals

def analyze_posts(username: str) -> List[Signal]:
    signals = []

    # FIXED: call posts.py function instead of itself
    post_results = fetch_posts(username)
    for p in post_results:
        signals.append(Signal(
            type="post",
            value=p["content"],
            confidence=p["confidence"],
            signal_type=p.get("signal_type", "INFERENCE"),
            evidence=p.get("evidence"),
            first_seen=p.get("first_seen"),
            last_seen=p.get("last_seen")
        ))

    return signals

def analyze_images_dir(image_dir: str) -> List[Signal]:
    img_results = analyze_images(image_dir)
    signals = []
    for i in img_results:
        signals.append(Signal(
            type="image",
            value=i["value"],
            confidence=i["confidence"],
            signal_type=i["signal_type"],
            evidence=i.get("evidence"),
            first_seen=i.get("first_seen"),
            last_seen=i.get("last_seen")
        ))
    return signals

def full_analysis(username: str, image_dir: str = None, include_temporal=True, include_stylometry=True):
    signals = []
    signals.extend(analyze_username(username))
    signals.extend(analyze_email(username))
    signals.extend(analyze_posts(username))

    if image_dir:
        signals.extend(analyze_images_dir(image_dir))

    # Apply inference labeling
    signals = apply_inference(signals)

    # Optional temporal analysis
    temporal_data = analyze_temporal(signals) if include_temporal else {}

    # Optional stylometry
    stylometry_data = analyze_stylometry(signals) if include_stylometry else {}

    return signals, temporal_data, stylometry_data
