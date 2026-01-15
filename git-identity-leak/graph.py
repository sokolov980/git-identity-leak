# git_identity_leak/graph.py
import networkx as nx
import json

def build_identity_graph(signals):
    """
    Build a graph from signals where each unique value is a node.
    """
    G = nx.Graph()
    for s in signals:
        if "value" not in s or "signal_type" not in s:
            continue
        node_id = f"{s['signal_type']}:{s['value']}"
        G.add_node(node_id, type=s['signal_type'], confidence=s.get('confidence', 'LOW'))

    # Connect all nodes to NAME nodes for identity mapping
    name_nodes = [f"{s['signal_type']}:{s['value']}" for s in signals if s.get("signal_type") == "NAME"]
    for n in name_nodes:
        for s in signals:
            if "value" in s:
                node_id = f"{s['signal_type']}:{s['value']}"
                if node_id != n:
                    G.add_edge(n, node_id)
    return G

def save_graph_json(graph, path):
    data = nx.node_link_data(graph)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
