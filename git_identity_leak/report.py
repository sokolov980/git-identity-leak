# git_identity_leak/report.py

import json
from datetime import datetime

def save_report(output_path, signals, temporal_data=None, stylometry_data=None):
    """
    Save the analysis report as JSON.

    Args:
        output_path (str): Path to save the report JSON.
        signals (list): List of collected identity signals.
        temporal_data (dict, optional): Temporal analysis results.
        stylometry_data (dict, optional): Stylometry analysis results.
    """
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "signals": signals or [],
        "temporal_data": temporal_data or {},
        "stylometry_data": stylometry_data or {},
    }

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    except Exception as e:
        print(f"[!] Failed to save report: {e}")
