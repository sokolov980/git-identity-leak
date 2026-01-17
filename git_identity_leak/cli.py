# git_identity_leak/cli.py
import argparse
import json
import os
from git_identity_leak.analysis import full_analysis
from git_identity_leak.graph import build_identity_graph, save_graph_json
from git_identity_leak.report import save_report

TRUNCATE_LEN = 120  # Increase so URLs are fully visible

def ascii_contrib_graph(yearly):
    """
    Create a simple ASCII graph for contributions per year.
    Each '#' represents ~5% of the maximum yearly contributions.
    """
    if not yearly:
        return ""
    max_count = max(yearly.values())
    lines = []
    for year, count in sorted(yearly.items()):
        bar_len = int((count / max_count) * 40) if max_count else 0
        bar = "#" * bar_len
        lines.append(f"{year}: {bar} ({count})")
    return "\n".join(lines)

def pretty_print_signals(signals, truncate_len=120):
    """
    Pretty print GitHub signals.
    Shows contributions, followers, following, mutuals, pronouns, GitHub Pages, languages.
    """
    print("[DEBUG] Signals:")
    if not signals:
        print("  No signals collected.")
        return

    headers = ["TYPE", "VALUE", "CONFIDENCE"]
    col_widths = [30, truncate_len, 10]
    divider = "-" * (sum(col_widths) + 4)
    print(divider)
    print(f"{headers[0]:<{col_widths[0]}} {headers[1]:<{col_widths[1]}} {headers[2]:<{col_widths[2]}}")
    print(divider)

    # Aggregate info
    contrib_total = None
    contrib_pattern = None
    contrib_years = {}
    followers = []
    following = []
    mutuals = []
    extra_info = []

    for s in signals:
        stype = s.get("signal_type", "UNKNOWN")
        value = str(s.get("value", ""))
        confidence = s.get("confidence", "")

        if stype == "CONTRIBUTION_TOTAL":
            contrib_total = value
            continue
        elif stype == "CONTRIBUTION_TIME_PATTERN":
            contrib_pattern = value
            continue
        elif stype == "CONTRIBUTIONS_YEAR":
            year = s.get("meta", {}).get("year", value)
            count = s.get("meta", {}).get("count", 0)
            contrib_years[year] = count
            continue
        elif stype == "FOLLOWER_USERNAME":
            followers.append(value)
            continue
        elif stype == "FOLLOWING_USERNAME":
            following.append(value)
            continue
        elif stype == "MUTUAL_CONNECTION":
            mutuals.append(value)
            continue
        elif stype in ("GITHUB_PAGES", "PRONOUNS", "PROFILE_PLATFORM", "LANGUAGE_PROFILE"):
            extra_info.append((stype, value, confidence))
            continue

        # REPO_SUMMARY
        if stype == "REPO_SUMMARY":
            parts = [p.strip() for p in value.split("|")]
            print(f"{stype:<{col_widths[0]}} {parts[0]:<{col_widths[1]}} {confidence:<{col_widths[2]}}")
            for part in parts[1:]:
                print(f"{'':<{col_widths[0]}} {part:<{col_widths[1]}}")
            continue

        display_value = value if len(value) <= truncate_len else value[:truncate_len-3] + "..."
        print(f"{stype:<{col_widths[0]}} {display_value:<{col_widths[1]}} {confidence:<{col_widths[2]}}")

    # Contributions
    if contrib_total is not None:
        print(f"{'CONTRIBUTION_TOTAL':<{col_widths[0]}} {contrib_total:<{col_widths[1]}} HIGH")
    if contrib_pattern is not None:
        print(f"{'CONTRIBUTION_TIME_PATTERN':<{col_widths[0]}} {contrib_pattern:<{col_widths[1]}} MEDIUM")
    if contrib_years:
        print("\n[Contributions per year]")
        print(ascii_contrib_graph(contrib_years))

    # Followers / Following / Mutuals
    if followers:
        print(f"\nFollowers ({len(followers)}): {', '.join(followers)}")
    if following:
        print(f"Following ({len(following)}): {', '.join(following)}")
    if mutuals:
        print(f"Mutual connections ({len(mutuals)}): {', '.join(mutuals)}")

    # Extra profile info
    for stype, value, confidence in extra_info:
        display_value = value if len(value) <= truncate_len else value[:truncate_len-3] + "..."
        print(f"{stype:<{col_widths[0]}} {display_value:<{col_widths[1]}} {confidence:<{col_widths[2]}}")

    print(divider)


def pretty_print_dict(title, d):
    print(f"[DEBUG] {title}:")
    if not d:
        print("  No data.")
        return
    print(json.dumps(d, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak OSINT Tool")
    parser.add_argument("--username", required=True, help="Target username to analyze")
    parser.add_argument("--self-audit", action="store_true", help="Run self-audit only")
    parser.add_argument("--images", help="Directory to store images")
    parser.add_argument("--graph-output", help="File to save graph JSON")
    parser.add_argument("--output", help="File to save report JSON")
    parser.add_argument("--temporal", action="store_true", help="Include temporal analysis")
    parser.add_argument("--stylometry", action="store_true", help="Include stylometry analysis")
    parser.add_argument("--verbose", action="store_true", help="Show debug output")
    args = parser.parse_args()

    if args.images:
        try:
            os.makedirs(args.images, exist_ok=True)
        except Exception as e:
            print(f"[!] Could not create image directory '{args.images}': {e}")
            args.images = None

    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_temporal=args.temporal,
        include_stylometry=args.stylometry
    )

    if args.verbose:
        pretty_print_signals(signals)
        pretty_print_dict("Temporal data", temporal_data)
        pretty_print_dict("Stylometry data", stylometry_data)

    graph = build_identity_graph(signals)
    if args.graph_output:
        save_graph_json(args.graph_output, graph)
        print(f"[+] Graph saved to {args.graph_output}")

    if args.output:
        save_report(args.output, signals, temporal_data, stylometry_data)
        print(f"[+] Report saved to {args.output}")


if __name__ == "__main__":
    main()
