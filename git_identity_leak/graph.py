# git_identity_leak/graph.py
import os
import networkx as nx
from networkx.readwrite import json_graph
import json

def build_identity_graph(signals):
    G = nx.Graph()

    # --- Base nodes ---
    for s in signals:
        stype = s.get("signal_type")
        value = s.get("value")
        if not stype or value is None:
            continue
        node_id = f"{stype}:{value}"
        G.add_node(node_id, **s)

    # --- Explicit follower/following edges ---
    username = next((s["value"] for s in signals if s["signal_type"] == "USERNAME"), None)
    if username:
        for s in signals:
            if s["signal_type"] in ("FOLLOWER_USERNAME", "FOLLOWING_USERNAME", "MUTUAL_CONNECTION"):
                G.add_edge(
                    f"USERNAME:{username}",
                    f"{s['signal_type']}:{s['value']}",
                    relation="SOCIAL_LINK"
                )

    # --- Repo nodes + edges ---
    repo_sigs = [s for s in signals if s.get("signal_type") == "REPO_SUMMARY"]
    inactivity_sigs = {s["value"].split(":")[0]: s for s in signals if s.get("signal_type") == "INACTIVITY_SCORE"}

    for repo in repo_sigs:
        repo_name = repo["value"].split("|")[0].strip()
        node_id = f"REPO:{repo_name}"

        # Merge repo data + inactivity
        node_data = repo.copy()
        if repo_name in inactivity_sigs:
            node_data["inactivity_score"] = inactivity_sigs[repo_name]["value"]

        G.add_node(node_id, **node_data)

        # Link to username
        if username:
            G.add_edge(f"USERNAME:{username}", node_id, relation="OWNS_REPO")

    # --- Contribution temporal graph ---
    contrib_years = [
        s for s in signals
        if s.get("signal_type") == "CONTRIBUTIONS_YEAR" and "meta" in s
    ]
    contrib_years.sort(key=lambda s: int(s["meta"]["year"]))

    prev_node = None
    for s in contrib_years:
        year = s["meta"]["year"]
        count = s["meta"]["count"]
        node_id = f"CONTRIBUTIONS_YEAR:{year}"

        # Add per-year node
        G.add_node(node_id, **s)

        # Link temporal edges
        if prev_node:
            G.add_edge(prev_node, node_id, relation="TEMPORAL_NEXT")
        prev_node = node_id

    # --- Contribution total node ---
    total_signal = next((s for s in signals if s["signal_type"] == "CONTRIBUTION_TOTAL"), None)
    if total_signal:
        G.add_node("CONTRIBUTION_TOTAL", **total_signal)

    # --- Contribution weekday/weekend pattern node ---
    pattern_signal = next((s for s in signals if s["signal_type"] == "CONTRIBUTION_TIME_PATTERN"), None)
    if pattern_signal:
        G.add_node("CONTRIBUTION_TIME_PATTERN", **pattern_signal)

        # Link pattern node to total contributions
        if total_signal:
            G.add_edge("CONTRIBUTION_TOTAL", "CONTRIBUTION_TIME_PATTERN", relation="PATTERN_REL")

    return G


def save_graph_json(path, G):
    if not isinstance(G, nx.Graph):
        raise TypeError("G must be a NetworkX graph, not a string")

    # Ensure directory exists
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    data = json_graph.node_link_data(G)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
