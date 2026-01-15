# git_identity_leak/cli.py
import argparse
from git_identity_leak.analysis import full_analysis
from git_identity_leak.report import save_report
from git_identity_leak.self_audit import self_audit
from git_identity_leak.graph import build_identity_graph, save_graph_json

def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak OSINT Tool")
    parser.add_argument("--username", required=True, help="Target username")
    parser.add_argument("--self-audit", action="store_true", help="Perform self-audit")
    parser.add_argument("--check-username", action="store_true", help="Check username reuse")
    parser.add_argument("--check-email", action="store_true", help="Check email reuse")
    parser.add_argument("--check-posts", action="store_true", help="Check posts on platforms")
    parser.add_argument("--images", help="Directory to store images")
    parser.add_argument("--graph-output", help="Output graph JSON path")
    parser.add_argument("--output", help="Output report JSON path")
    parser.add_argument("--temporal", action="store_true", help="Include temporal analysis")
    parser.add_argument("--stylometry", action="store_true", help="Include stylometry analysis")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.self_audit:
        signals = self_audit(args.username)
        if args.verbose:
            print(signals)
        return

    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_stylometry=args.stylometry,
        include_temporal=args.temporal
    )

    if args.graph_output:
        graph = build_identity_graph(signals)
        save_graph_json(graph, args.graph_output)

    if args.output:
        save_report(signals, temporal_data, stylometry_data, args.output)

    if args.verbose:
        print("[DEBUG] Signals:", signals)
        print("[DEBUG] Temporal data:", temporal_data)
        print("[DEBUG] Stylometry data:", stylometry_data)

if __name__ == "__main__":
    main()
