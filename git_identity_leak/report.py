# git_identity_leak/report.py
import json

def save_report(filepath, signals, temporal_data=None, stylometry_data=None):
    """
    Save a structured JSON report including signals, temporal data, and stylometry.
    
    Args:
        filepath (str): Path to save the report file.
        signals (list): Collected identity signals.
        temporal_data (dict, optional): Temporal analysis results.
        stylometry_data (dict, optional): Stylometry analysis results.
    """
    report = {
        "signals": signals,
        "temporal_data": temporal_data if temporal_data else {},
        "stylometry_data": stylometry_data if stylometry_data else {}
    }

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Failed to save report to {filepath}: {e}")
