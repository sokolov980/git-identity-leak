import networkx as nx
from schemas import Signal
from typing import List
from networkx.readwrite import json_graph
import json

def build_identity_graph(signals: List[Signal]) -> nx.Graph:
    """
    Builds a confidence-weighted identity graph from signals.
    Nodes: type:value
    Edges: weighted by min confidence of connected nodes
    """
    G = nx.Graph()

    # Add nodes
    for s in signals:
        node_id = f"{s.type}:{s.value}"
        G.add_node(
            node_id,
            type=s.type,
            confidence=s.confidence,
            signal_type=s.signal_type,
            evidence=s.evidence,
            first_seen=s.first_seen,
            last_seen=s.last_seen
        )

    # Add edges (connect nodes of different types)
    for i, a in enumerate(signals):
        for j, b in enumerate(signals):
            if i >= j or a.type == b.type:
                continue
            weight = min(a.confidence, b.confidence)
            if weight > 0.2:  # threshold to avoid clutter
                G.add_edge(
                    f"{a.type}:{a.value}",
                    f"{b.type}:{b.value}",
                    weight=weight
                )
    return G

def save_graph_json(G: nx.Graph, path: str):
    data = json_graph.node_link_data(G)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_graph_json(path: str) -> nx.Graph:
    with open(path) as f:
        data = json.load(f)
    return json_graph.node_link_graph(data)
