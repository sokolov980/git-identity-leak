# git_identity_leak/graph.py
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

    # Connect nodes with the same value
    for i, s1 in enumerate(signals):
        for j, s2 in enumerate(signals):
            if i >= j:
                continue
            if s1.get("value") == s2.get("value"):
                n1 = f"{s1.get('signal_type')}:{s1.get('value')}"
                n2 = f"{s2.get('signal_type')}:{s2.get('value')}"
                G.add_edge(n1, n2)

    return G

def save_graph_json(path, G):
    if not isinstance(G, nx.Graph):
        raise TypeError("G must be a NetworkX graph, not a string")
    data = json_graph.node_link_data(G)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
