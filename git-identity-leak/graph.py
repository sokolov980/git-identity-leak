# git_identity_leak/graph.py

import networkx as nx
import json
from networkx.readwrite import json_graph

def build_identity_graph(signals):
    """
    Build a NetworkX graph from identity signals.

    Each signal should be a dict with keys:
      - signal_type (str): e.g., "username", "email", "image"
      - value (str)
      - confidence (float, optional)
    
    Returns:
        G (networkx.Graph): Identity graph
    """
    G = nx.Graph()
    
    for s in signals:
        # Convert dict signal to graph node
        node_id = f"{s['signal_type']}:{s['value']}"
        G.add_node(node_id, **s)

    # Example: Connect username to email if both exist
    usernames = [s for s in signals if s['signal_type'] == 'username']
    emails = [s for s in signals if s['signal_type'] == 'email']
    images = [s for s in signals if s['signal_type'] == 'image']

    # Connect usernames to emails
    for u in usernames:
        u_id = f"{u['signal_type']}:{u['value']}"
        for e in emails:
            e_id = f"{e['signal_type']}:{e['value']}"
            G.add_edge(u_id, e_id)

    # Connect usernames to images
    for u in usernames:
        u_id = f"{u['signal_type']}:{u['value']}"
        for img in images:
            img_id = f"{img['signal_type']}:{img['value']}"
            G.add_edge(u_id, img_id)

    return G

def save_graph_json(G, filepath):
    """
    Save a NetworkX graph as a JSON file using node-link format.
    """
    data = json_graph.node_link_data(G)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
