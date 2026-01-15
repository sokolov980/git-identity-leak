# self_audit.py

from analysis import analyze_username, analyze_email, analyze_posts

def self_audit(username):
    """
    Simple self-audit that checks username, email, and posts.
    Prints a report summary.
    """
    signals = []

    # Collect signals
    signals.extend(analyze_username(username))
    signals.extend(analyze_email(username))
    signals.extend(analyze_posts(username))

    # Calculate a simple risk score (example)
    risk_score = 0
    for s in signals:
        risk_score += s.get("confidence", 0)

    # Normalize risk (0–1)
    risk_score = min(risk_score / 3, 1.0)

    print("\n=== SELF-AUDIT REPORT ===")
    print(f"Overall re-identification risk: {'HIGH' if risk_score > 0.7 else 'MEDIUM' if risk_score > 0.4 else 'LOW'}")
    print("Key drivers:")
    for s in signals:
        print(f" - {s['signal_type'].capitalize()}: {s['value']} (score {s['confidence']})")
    print("==========================\n")
