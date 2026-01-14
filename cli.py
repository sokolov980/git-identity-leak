import argparse
from github_api import fetch_commit_metadata
from analysis import analyze_commits
from report import print_report, save_json
from images import analyze_images
from reuse import check_username, check_email
from posts import analyze_posts
from graph import build_identity_graph, save_graph_json

def main():
    parser = argparse.ArgumentParser(description="Full OSINT identity analyzer")
    parser.add_argument("--username", required=True, help="GitHub username to analyze")
    parser.add_argument("--max-commits", type=int, default=50)
    parser.add_argument("--images", help="Folder with images to analyze")
    parser.add_argument("--check-username", action="store_true")
    parser.add_argument("--check-email", action="store_true")
    parser.add_argument("--check-posts", action="store_true", help="Analyze public posts")
    parser.add_argument("--output", help="JSON report file")
    parser.add_argument("--graph-output", help="Save identity graph JSON")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    commits = fetch_commit_metadata(args.username, max_commits=args.max_commits)
    findings = analyze_commits(args.username, commits) if commits else {}

    if args.images:
        findings["images"] = analyze_images(args.images)

    if args.check_username:
        findings["username_reuse"] = check_username(args.username)

    if args.check_email and commits:
        email = None
        for c in commits:
            if c.get("author_email"):
                email = c["author_email"]
                break
        findings["email_reuse"] = check_email(email)

    if args.check_posts:
        findings["posts"] = analyze_posts(args.username)

    print_report(args.username, findings, verbose=args.verbose)

    if args.output:
        save_json(findings, args.output)

    if args.graph_output:
        G = build_identity_graph(findings)
        save_graph_json(G, args.graph_output)
        if args.verbose:
            print(f"[DEBUG] Graph saved to {args.graph_output}")

if __name__ == "__main__":
    main()
