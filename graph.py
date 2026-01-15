import networkx as nx
from schemas import Signal

def build_identity_graph(signals: list[Signal]):
    G = nx.Graph()
    for s in signals:
        node_id = f"{s.type}:{s.value}"
        G.add_node(node_id, type=s.type, confidence=s.confidence, signal_type=s.signal_type, evidence=s.evidence)
    # Connect nodes with weighted edges if confidence > 0.5
    for i, a in enumerate(signals):
        for j, b in enumerate(signals):
            if i >= j:
                continue
            weight = min(a.confidence, b.confidence)
            if weight > 0.5:
                G.add_edge(f"{a.type}:{a.value}", f"{b.type}:{b.value}", weight=weight)
    return G

def save_graph_json(G, path: str):
    import json
    from networkx.readwrite import json_graph
    data = json_graph.node_link_data(G)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
