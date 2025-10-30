
from typing import List, Dict
import matplotlib.pyplot as plt
import networkx as nx

def plot_graph(G: nx.Graph, ax=None):
    if ax is None:
        _, ax = plt.subplots()
    pos = nx.get_node_attributes(G, "pos")
    nx.draw(G, pos=pos, with_labels=False, node_size=120, ax=ax)
    labels = {n: G.nodes[n]["name"] for n in G.nodes}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, ax=ax)
    return ax

def plot_route(G: nx.Graph, route_nodes: List[int], title: str = "Rota"):
    fig, ax = plt.subplots()
    plot_graph(G, ax=ax)
    pos = nx.get_node_attributes(G, "pos")
    path_edges = list(zip(route_nodes[:-1], route_nodes[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=3, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=route_nodes, node_size=180, ax=ax)
    ax.set_title(title)
    fig.tight_layout()
    return fig
