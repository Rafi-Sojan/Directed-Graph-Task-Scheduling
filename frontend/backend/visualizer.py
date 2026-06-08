import networkx as nx
import matplotlib.pyplot as plt
from textwrap import fill


def _dag_layout(graph):
    try:
        generations = list(nx.topological_generations(graph))
    except nx.NetworkXUnfeasible:
        return nx.spring_layout(graph, seed=42)

    positions = {}
    for layer_index, layer in enumerate(generations):
        layer_nodes = list(layer)
        y_offset = (len(layer_nodes) - 1) / 2
        for row_index, node in enumerate(layer_nodes):
            positions[node] = (layer_index, y_offset - row_index)

    return positions


def draw_graph(tasks, graph, title="Task Dependency Graph"):
    directed_graph = nx.DiGraph()

    for t in tasks:
        directed_graph.add_node(t["task"])

    for u in graph:
        for v in graph[u]:
            directed_graph.add_edge(u, v)

    if not directed_graph.nodes:
        figure, axis = plt.subplots(figsize=(8, 4))
        axis.text(0.5, 0.5, "Add tasks to visualize the graph", ha="center", va="center")
        axis.axis("off")
        return figure

    pos = _dag_layout(directed_graph)
    node_colors = [
        "#4f46e5" if directed_graph.in_degree(node) == 0 else "#14b8a6"
        for node in directed_graph.nodes
    ]
    labels = {node: fill(node, width=14) for node in directed_graph.nodes}
    node_count = directed_graph.number_of_nodes()
    node_size = max(900, min(3200, int(17000 / max(node_count, 1))))
    font_size = 8 if node_count <= 8 else 7

    figure, axis = plt.subplots(figsize=(10, 5.5))
    nx.draw(
        directed_graph,
        pos,
        ax=axis,
        with_labels=False,
        node_color=node_colors,
        node_size=node_size,
        edge_color="#64748b",
        arrows=True,
        arrowsize=20,
        width=2,
        connectionstyle="arc3,rad=0.03",
    )
    nx.draw_networkx_labels(
        directed_graph,
        pos,
        labels=labels,
        ax=axis,
        font_size=font_size,
        font_weight="bold",
        font_color="#0f172a",
    )
    axis.set_title(title)
    x_values = [point[0] for point in pos.values()]
    y_values = [point[1] for point in pos.values()]
    axis.set_xlim(min(x_values) - 0.8, max(x_values) + 0.8)
    axis.set_ylim(min(y_values) - 0.8, max(y_values) + 0.8)
    axis.axis("off")

    return figure
