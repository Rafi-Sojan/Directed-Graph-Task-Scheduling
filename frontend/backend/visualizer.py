import networkx as nx
import matplotlib.pyplot as plt

def draw_graph(tasks, graph):
    G = nx.DiGraph()

    priority_map = {}
    for t in tasks:
        name = t["task"]
        priority = int(t["priority"].split()[1])
        priority_map[name] = priority
        G.add_node(name)

    for u in graph:
        for v in graph[u]:
            G.add_edge(u, v)

    pos = nx.spring_layout(G, seed=42)

    colors = []
    for node in G.nodes():
        p = priority_map[node]
        if p == 1:
            colors.append("red")
        elif p == 2:
            colors.append("orange")
        else:
            colors.append("green")

    plt.figure(figsize=(8, 6))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=colors,
        node_size=2000,
        font_size=10,
        font_weight="bold",
        arrows=True
    )

    return plt