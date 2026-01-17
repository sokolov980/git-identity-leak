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
        if not stype or not value:
            continue
        node_id = f"{stype}:{value}"
        G.add_node(node_id, **s)

    # --- Explicit follower/following edges ---
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

    # --- Contribution temporal graph ---
    contrib_years = [
        s for s in signals
        if s.get("signal_type") == "CONTRIBUTIONS_YEAR"
        and "meta" in s
    ]

    # Sort by year
    contrib_years.sort(key=lambda s: int(s["meta"]["year"]))

    prev_node = None
    for s in contrib_years:
        year = s["meta"]["year"]
        count = s["meta"]["count"]

        node_id = f"CONTRIBUTIONS_YEAR:{year}"

        G.nodes[node_id]["year"] = year
        G.nodes[node_id]["count"] = count

        if prev_node:
            G.add_edge(
                prev_node,
                node_id,
                relation="TEMPORAL_NEXT"
            )

        prev_node = node_id

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
