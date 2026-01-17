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

    # --- Explicit follower/following/mutual edges ---
    username = next(
        (s["value"] for s in signals if s["signal_type"] == "USERNAME"),
        None
    )
    if username:
        for s in signals:
            if s["signal_type"] in (
                "FOLLOWER_USERNAME",
                "FOLLOWING_USERNAME",
                "MUTUAL_CONNECTION"
            ):
                G.add_edge(
                    f"USERNAME:{username}",
                    f"{s['signal_type']}:{s['value']}",
                    relation="SOCIAL_LINK"
                )

    # --- Contributions temporal graph ---
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
        G.nodes[node_id]["year"] = year
        G.nodes[node_id]["count"] = count

        # Link years sequentially
        if prev_node:
            G.add_edge(prev_node, node_id, relation="TEMPORAL_NEXT")
        prev_node = node_id

    # --- Contribution total ---
    total_contrib = next(
        (s["value"] for s in signals if s["signal_type"] == "CONTRIBUTION_TOTAL"),
        None
    )
    if total_contrib is not None:
        node_id = f"CONTRIBUTION_TOTAL:{total_contrib}"
        G.add_node(node_id, signal_type="CONTRIBUTION_TOTAL", value=total_contrib)
        # Link total to first year
        if contrib_years:
            first_year_node = f"CONTRIBUTIONS_YEAR:{contrib_years[0]['meta']['year']}"
            G.add_edge(node_id, first_year_node, relation="TOTAL_TO_YEAR")

    # --- Contribution time pattern ---
    time_pattern = next(
        (s["value"] for s in signals if s["signal_type"] == "CONTRIBUTION_TIME_PATTERN"),
        None
    )
    if time_pattern is not None:
        node_id = f"CONTRIBUTION_TIME_PATTERN:{time_pattern}"
        G.add_node(node_id, signal_type="CONTRIBUTION_TIME_PATTERN", value=time_pattern)
        # Connect to total contributions if exists
        if total_contrib is not None:
            total_node = f"CONTRIBUTION_TOTAL:{total_contrib}"
            G.add_edge(node_id, total_node, relation="PATTERN_TO_TOTAL")

    return G

def save_graph_json(path, G):
    if not isinstance(G, nx.Graph):
        raise TypeError("G must be a NetworkX graph, not a string")

    # Only make directories if a directory is specified
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    data = json_graph.node_link_data(G)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
