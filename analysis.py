from github_api import fetch_commits
from reuse import check_username_reuse, check_email_reuse
from images import analyze_images
from posts import analyze_posts
from schemas import Signal

def analyze_username(username: str):
    signals = []
    # Collect reuse across platforms
    reuse_results = check_username_reuse(username)
    for r in reuse_results:
        signals.append(Signal(
            type="username",
            value=username,
            confidence=r["confidence"],
            signal_type="FACT" if r["found"] else "INFERENCE",
            evidence=r.get("evidence", "Platform check"),
            first_seen=r.get("first_seen"),
            last_seen=r.get("last_seen")
        ))
    return signals

def analyze_email(username: str):
    signals = []
    email_results = check_email_reuse(username)
    for r in email_results:
        signals.append(Signal(
            type="email",
            value=r["value"],
            confidence=r["confidence"],
            signal_type="FACT" if r["found"] else "INFERENCE",
            evidence=r.get("evidence", "Email reuse check"),
            first_seen=r.get("first_seen"),
            last_seen=r.get("last_seen")
        ))
    return signals

def analyze_posts(username: str):
    post_signals = analyze_posts(username)
    signals = []
    for p in post_signals:
        signals.append(Signal(
            type="post",
            value=p["content"],
            confidence=p["confidence"],
            signal_type="INFERENCE",
            evidence=p.get("evidence"),
            first_seen=p.get("first_seen"),
            last_seen=p.get("last_seen")
        ))
    return signals
