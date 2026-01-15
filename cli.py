import argparse
from analysis import analyze_username, analyze_email, analyze_posts
from graph import build_identity_graph, save_graph_json
from report import generate_report
from risk import compute_risk
from inference import apply_inference
from self_audit import self_audit

def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak OSINT Tool")
    parser.add_argument("--username", type=str, help="Username to analyze", required=False)
    parser.add_argument("--check-username", action="store_true")
    parser.add_argument("--check-email", action="store_true")
    parser.add_argument("--check-posts", action="store_true")
    parser.add_argument("--graph-output", type=str, help="Save identity graph JSON")
    parser.add_argument("--output", type=str, help="Save structured report JSON")
    parser.add_argument("--self-audit", action="store_true")
    parser.add_argument("--temporal", action="store_true")
    parser.add_argument("--stylometry", action="store_true")
    parser.add_argument("--plugins", nargs="*", help="Specify plugin modules to run")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.self_audit:
        self_audit()

    findings = []

    if args.check_username and args.username:
        username_signals = analyze_username(args.username)
        findings.extend(username_signals)

    if args.check_email and args.username:
        email_signals = analyze_email(args.username)
        findings.extend(email_signals)

    if args.check_posts and args.username:
        post_signals = analyze_posts(args.username)
        findings.extend(post_signals)

    # Apply inference logic
    findings = apply_inference(findings)

    # Build identity graph
    graph = build_identity_graph(findings)

    if args.graph_output:
        save_graph_json(graph, args.graph_output)

    # Compute risk scores
    risk_summary = compute_risk(findings, graph)

    # Generate report
    if args.output:
        generate_report(findings, risk_summary, args.output)

    if args.verbose:
        print("[DEBUG] Findings:", findings)
        print("[DEBUG] Risk summary:", risk_summary)

if __name__ == "__main__":
    main()
