from analysis import full_analysis
from risk import summarize_risk

def self_audit(username):
    signals, temporal_data, stylometry_data = full_analysis(username)
    risk_summary = summarize_risk(signals)
    print("=== SELF-AUDIT REPORT ===")
    print(f"Overall re-identification risk: {risk_summary['overall_risk']}")
    print("Key drivers:")
    for d in risk_summary.get("drivers", []):
        print(f" - {d['driver']} (score {d['score']})")
    print("==========================")
