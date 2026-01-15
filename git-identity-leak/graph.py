# git-identity-leak/graph.py

import networkx as nx
import json
from networkx.readwrite import json_graph

def build_identity_graph(signals):
    """
    Build a NetworkX graph from signals.
    """
    G = nx.Graph()

    for s in signals:
        value = s.get("value")
        signal_type = s.get("signal_type", "unknown")
        if not value:
            continue
        node_id = f"{signal_type}:{value}"
        G.add_node(node_id, **s)

    # Connect usernames to emails and images
    usernames = [s for s in signals if s.get('signal_type') == 'username' and s.get('value')]
    emails = [s for s in signals if s.get('signal_type') == 'email' and s.get('value')]
    images = [s for s in signals if s.get('signal_type') == 'image' and s.get('value')]

    for u in usernames:
        u_id = f"{u['signal_type']}:{u['value']}"
        for e in emails:
            e_id = f"{e['signal_type']}:{e['value']}"
            G.add_edge(u_id, e_id)
        for img in images:
            img_id = f"{img['signal_type']}:{img['value']}"
            G.add_edge(u_id, img_id)

    return G

def save_graph_json(G, filepath):
    data = json_graph.node_link_data(G)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
