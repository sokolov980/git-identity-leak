# git_identity_leak/self_audit.py
from git_identity_leak.analysis import full_analysis

def self_audit(username):
    """
    Perform a basic self-audit on a username.
    """
    signals, temporal_data, stylometry_data = full_analysis(
        username=username,
        include_stylometry=False,
        include_temporal=True
    )
    print("=== SELF-AUDIT REPORT ===")
    print(f"Overall re-identification risk: {max([s.get('confidence','LOW') for s in signals], default='LOW')}")
    print("Key drivers:")
    for s in signals:
        if s.get("signal_type") in ["NAME", "USERNAME", "EMAIL"]:
            print(f" - {s.get('signal_type')}: {s.get('value')} (score {s.get('confidence','LOW')})")
    print("==========================")
    return signals
