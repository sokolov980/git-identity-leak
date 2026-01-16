# git_identity_leak/graph.py

import networkx as nx
import json

def build_identity_graph(signals):
    """
    Build a graph connecting usernames, emails, and images from signals.
    Each node is a unique identity element, edges indicate possible connections.
    """
    G = nx.Graph()

    for s in signals:
        # Safely access signal_type and value
        signal_type = s.get("signal_type")
        value = s.get("value")
        if not signal_type or not value:
            continue

        node_id = f"{signal_type}:{value}"
        G.add_node(node_id, type=signal_type, value=value, confidence=s.get("confidence"))

    # Simple edges: connect all signals from same type (can improve later)
    nodes = list(G.nodes)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            G.add_edge(nodes[i], nodes[j])

    return G

def save_graph_json(G, output_path):
    """
    Save a NetworkX graph to JSON (node-link format).
    """
    data = nx.node_link_data(G)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
