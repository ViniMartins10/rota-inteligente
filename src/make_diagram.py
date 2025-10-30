from pathlib import Path
import pandas as pd
import networkx as nx
from src.graph_utils import load_city_graph
from src.visualize import plot_graph

def main(base="."):
    base = Path(base)
    G = load_city_graph(base/"data"/"nodes.csv", base/"data"/"edges.csv")
    fig = plot_graph(G)
    fig.figure.savefig(base/"outputs"/"diagrama_grafo.png")

if __name__ == "__main__":
    main(".")
