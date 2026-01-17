# git_identity_leak/graph.py
import os
import networkx as nx
from networkx.readwrite import json_graph
import json

def build_identity_graph(signals):
    G = nx.Graph()

    for s in signals:
        stype = s.get("signal_type")
        value = s.get("value")
        if not stype or not value:
            continue
        node_id = f"{stype}:{value}"
        G.add_node(node_id, **s)

    # Explicit follower/following edges
    for s in signals:
        if s["signal_type"] in ("FOLLOWER_USERNAME", "FOLLOWING_USERNAME"):
            user = next(
                (x["value"] for x in signals if x["signal_type"] == "USERNAME"),
                None
            )
            if user:
                G.add_edge(
                    f"USERNAME:{user}",
                    f"{s['signal_type']}:{s['value']}"
                )

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
