import json

def generate_report(signals, risk_summary, path: str):
    report = {
        "signals": [s.__dict__ for s in signals],
        "risk_summary": risk_summary
    }
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
