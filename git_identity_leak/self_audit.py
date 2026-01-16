from git_identity_leak.analysis import full_analysis


def self_audit(username):
    signals, temporal, stylometry = full_analysis(username)
    print("[+] Self-audit complete")
    print("Signals found:", len(signals))
