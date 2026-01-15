# git-identity-leak/self_audit.py

from analysis import full_analysis
from report import save_report
from graph import build_identity_graph, save_graph_json

# Optional terminal colors
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

def pretty_print_self_audit(signals):
    if not signals:
        print(" - No signals found during self-audit.")
        return
    print("\n[DEBUG] Signals collected during self-audit:")
    for s in signals:
        signal_type = s.get("signal_type", "unknown")
        value = s.get("value", "N/A")
        confidence = s.get("confidence", "N/A")
        print(f" - {signal_type}: {value} (confidence={confidence})")

def self_audit(username, image_dir=None, graph_output=None, report_output=None):
    """
    Perform a self-audit for the given username.

    Args:
        username (str): Your GitHub username (or target for self-audit)
        image_dir (str, optional): Directory to save images
        graph_output (str, optional): Path to save graph JSON
        report_output (str, optional): Path to save JSON report
    """
    print(f"{Colors.YELLOW}=== SELF-AUDIT REPORT FOR '{username}' ==={Colors.RESET}")

    # Run full analysis
    signals, temporal_data, stylometry_data = full_analysis(
        username=username,
        image_dir=image_dir,
        include_temporal=True,
        include_stylometry=True
    )

    # Save outputs if specified
    if graph_output:
        graph = build_identity_graph(signals)
        save_graph_json(graph, graph_output)
        print(f"{Colors.GREEN}[+] Graph saved to {graph_output}{Colors.RESET}")

    if report_output:
        save_report(signals, temporal_data, stylometry_data, report_output)
        print(f"{Colors.GREEN}[+] Report saved to {report_output}{Colors.RESET}")

    # Pretty-print collected signals
    pretty_print_self_audit(signals)

    # Basic risk summary
    risk_drivers = [s for s in signals if s.get("confidence") in ("HIGH", "MEDIUM")]
    overall_risk = "HIGH" if any(d.get("confidence") == "HIGH" for d in risk_drivers) else "MEDIUM"
    print(f"\n[+] Overall re-identification risk: {Colors.RED if overall_risk=='HIGH' else Colors.YELLOW}{overall_risk}{Colors.RESET}")

    if risk_drivers:
        print("Key drivers:")
        for s in risk_drivers:
            print(f" - {s.get('signal_type')}: {s.get('value')} (confidence={s.get('confidence')})")

    print(f"{Colors.YELLOW}=========================={Colors.RESET}")
