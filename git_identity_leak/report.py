import json
import os

def save_report(output_path, signals, temporal_data=None, stylometry_data=None):
    """
    Save the OSINT report to a JSON file.

    Args:
        output_path (str): Path to save JSON report
        signals (list): List of all identity signals
        temporal_data (dict, optional): Temporal analysis results
        stylometry_data (dict, optional): Stylometry analysis results
    """
    report = {
        "signals": signals,
        "temporal_data": temporal_data if temporal_data else {},
        "stylometry_data": stylometry_data if stylometry_data else {}
    }

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print(f"[+] Report saved to {output_path}")
