# git-identity-leak/self_audit.py

from analysis import full_analysis

def self_audit(username):
    signals, temporal_data, stylometry_data = full_analysis(username)
    print(f"=== SELF-AUDIT REPORT for {username} ===")
    print(f"Overall signals found: {len(signals)}")
    for s in signals:
        print(f" - {s['signal_type']}: {s.get('value')} (confidence={s.get('confidence')})")
    print("==========================")
