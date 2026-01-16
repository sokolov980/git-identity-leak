import networkx as nx
from networkx.readwrite import json_graph
import json

def build_identity_graph(signals):
    G = nx.Graph()
    for s in signals:
        if "value" not in s or "signal_type" not in s:
            continue
        node_id = f"{s['signal_type']}:{s['value']}"
        G.add_node(node_id, **s)
    return G

def save_graph_json(G, output_path):
    data = json_graph.node_link_data(G)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Graph saved to {output_path}")
