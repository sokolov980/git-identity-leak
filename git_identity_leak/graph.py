import json
import networkx as nx


def build_identity_graph(signals):
    G = nx.Graph()

    entity_node = "ENTITY:target"
    G.add_node(entity_node, label="Target")

    for s in signals:
        if "signal_type" not in s or "value" not in s:
            continue

        node_id = f"{s['signal_type']}:{s['value']}"
        G.add_node(node_id, label=s["value"], type=s["signal_type"])
        G.add_edge(entity_node, node_id)

    return G


def save_graph_json(graph, path):
    data = nx.node_link_data(graph)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
