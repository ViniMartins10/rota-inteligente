
import math
import pandas as pd
import networkx as nx

def load_city_graph(nodes_path: str, edges_path: str) -> nx.Graph:
    nodes = pd.read_csv(nodes_path)
    edges = pd.read_csv(edges_path)

    G = nx.Graph()
    for _, row in nodes.iterrows():
        G.add_node(int(row["id"]), name=row["name"], pos=(float(row["x"]), float(row["y"])))

    for _, row in edges.iterrows():
        u, v = int(row["source"]), int(row["target"])
        d = float(row["distance_km"])
        speed = float(row["speed_kmh"])
        time_h = d / speed if speed > 0 else math.inf
        G.add_edge(u, v, distance_km=d, speed_kmh=speed, time_h=time_h)
    return G

def euclidean_heuristic(G: nx.Graph, n1: int, n2: int) -> float:
    (x1, y1) = G.nodes[n1]["pos"]
    (x2, y2) = G.nodes[n2]["pos"]
    return math.hypot(x2 - x1, y2 - y1)
