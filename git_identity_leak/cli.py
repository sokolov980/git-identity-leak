import argparse
from git_identity_leak.analysis import full_analysis
from git_identity_leak.report import save_report
from git_identity_leak.self_audit import self_audit
from git_identity_leak.graph import build_identity_graph, save_graph_json


def main():
    parser = argparse.ArgumentParser(description="git-identity-leak OSINT tool")

    parser.add_argument("--username", required=True)
    parser.add_argument("--self-audit", action="store_true")
    parser.add_argument("--check-username", action="store_true")
    parser.add_argument("--check-email", action="store_true")
    parser.add_argument("--check-posts", action="store_true")
    parser.add_argument("--images")
    parser.add_argument("--graph-output")
    parser.add_argument("--output")
    parser.add_argument("--temporal", action="store_true")
    parser.add_argument("--stylometry", action="store_true")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.self_audit:
        self_audit(args.username)
        return

    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_temporal=args.temporal,
        include_stylometry=args.stylometry,
    )

    if args.graph_output:
        graph = build_identity_graph(signals)
        save_graph_json(graph, args.graph_output)
        print(f"[+] Graph saved to {args.graph_output}")

    if args.output:
        save_report(
            args.output,
            signals,
            temporal_data,
            stylometry_data,
        )
        print(f"[+] Report saved to {args.output}")

    if args.verbose:
        print("[DEBUG] Signals:", signals)
        print("[DEBUG] Temporal data:", temporal_data)
        print("[DEBUG] Stylometry data:", stylometry_data)

    print("[+] Analysis complete.")


if __name__ == "__main__":
    main()
