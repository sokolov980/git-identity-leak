import json

def save_report(path, signals, temporal_data, stylometry_data):
    report = {
        "signals": signals,
        "temporal": temporal_data,
        "stylometry": stylometry_data
    }
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[+] Report saved to {path}")
