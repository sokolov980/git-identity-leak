from analysis import analyze_username, analyze_email, analyze_posts
from graph import build_identity_graph
from risk import compute_risk
from inference import apply_inference

def self_audit(username: str = None):
    """
    Runs a full analysis on yourself and outputs actionable leaks.
    """
    if not username:
        print("[!] Please provide a username for self-audit.")
        return

    signals = []
    signals.extend(analyze_username(username))
    signals.extend(analyze_email(username))
    signals.extend(analyze_posts(username))

    signals = apply_inference(signals)
    graph = build_identity_graph(signals)
    risk_summary = compute_risk(signals, graph)

    print("\n=== SELF-AUDIT REPORT ===")
    print(f"Overall re-identification risk: {risk_summary['overall_risk']}")
    print("Key drivers:")
    for d in risk_summary["drivers"]:
        print(f" - {d['driver']} (score {d['score']:.2f})")
    print("==========================\n")
