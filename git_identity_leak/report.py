import json
from pathlib import Path


def save_report(report_data, output_path):
    """
    Save analysis report as JSON.

    Args:
        report_data (dict): Full analysis report
        output_path (str): Path to output JSON file
    """
    try:
        path = Path(output_path)
        with path.open("w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        print(f"[+] Report saved to {output_path}")
    except Exception as e:
        print(f"[!] Failed to save report: {e}")
