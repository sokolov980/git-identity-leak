from git_identity_leak.analysis import full_analysis
from git_identity_leak.risk import summarize_risk


def self_audit(username):
    signals, _, _ = full_analysis(username)

    summary = summarize_risk(signals)

    print("\n=== SELF-AUDIT REPORT ===")
    print(f"Overall re-identification risk: {summary['overall_risk']}")
    print("Key drivers:")
    for d in summary["drivers"]:
        print(f" - {d['driver']} (score {d['score']})")
    print("==========================\n")
