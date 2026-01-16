# git_identity_leak/self_audit.py
from git_identity_leak.analysis import full_analysis
from git_identity_leak.risk import summarize_risk
from git_identity_leak.report import save_report

def self_audit(username):
    signals, temporal_data, stylometry_data = full_analysis(username)
    risk_summary = summarize_risk(signals)
    print("=== SELF-AUDIT REPORT ===")
    print(f"Overall re-identification risk: {risk_summary.get('overall_risk', 'UNKNOWN')}")
    print("Key drivers:")
    for driver in risk_summary.get("drivers", []):
        print(f" - {driver['driver']} (score {driver['score']})")
    print("==========================")
    # Optionally save report
    save_report(f"{username}_self_audit.json", signals, temporal_data, stylometry_data)
