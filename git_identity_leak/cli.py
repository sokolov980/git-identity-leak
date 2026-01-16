# git_identity_leak/cli.py

import argparse
from git_identity_leak.analysis import full_analysis
from git_identity_leak.report import save_report
from git_identity_leak.graph import build_identity_graph

def parse_args():
    parser = argparse.ArgumentParser(description="Git Identity Leak OSINT Tool")
    parser.add_argument("--username", required=True)
    parser.add_argument("--self-audit", action="store_true")
    parser.add_argument("--images", type=str)
    parser.add_argument("--graph-output", type=str)
    parser.add_argument("--output", type=str)
    parser.add_argument("--temporal", action="store_true")
    parser.add_argument("--stylometry", action="store_true")
    parser.add_argument("--verbose", action="store_true")

    # Add new flags
    parser.add_argument("--check-username", action="store_true")
    parser.add_argument("--check-email", action="store_true")
    parser.add_argument("--check-posts", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_temporal=args.temporal,
        include_stylometry=args.stylometry,
        check_username=args.check_username,
        check_email=args.check_email,
        check_posts=args.check_posts
    )

    if args.graph_output:
        graph = build_identity_graph(signals)
        import json
        with open(args.graph_output, "w") as f:
            json.dump(graph, f)
        print(f"[+] Graph saved to {args.graph_output}")

    if args.output:
        save_report(args.output, signals, temporal_data, stylometry_data)
        print(f"[+] Report saved to {args.output}")


if __name__ == "__main__":
    main()
