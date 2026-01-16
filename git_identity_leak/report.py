# report.py

import json
from datetime import datetime

def save_report(signals, temporal_data, stylometry_data, filepath):
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "signals": signals,
        "temporal": temporal_data,
        "stylometry": stylometry_data
    }
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"[+] Report successfully saved to {filepath}")
    except Exception as e:
        print(f"[!] Failed to save report: {e}")
