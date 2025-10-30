# src/routing.py
from typing import List, Tuple, Dict
import itertools
import networkx as nx
from .graph_utils import euclidean_heuristic

def a_star_path(G: nx.Graph, src: int, dst: int, weight: str = "distance_km") -> List[int]:
    return nx.astar_path(G, src, dst, heuristic=lambda u, v: euclidean_heuristic(G, u, v), weight=weight)

def path_length(G: nx.Graph, path: List[int], weight: str = "distance_km") -> float:
    return sum(G.edges[u, v][weight] for u, v in zip(path[:-1], path[1:]))

def nearest_neighbor_tsp(G: nx.Graph, nodes: List[int], start: int, weight: str = "distance_km") -> List[int]:
    remaining = set(nodes)
    route = [start]
    remaining.discard(start)
    current = start
    while remaining:
        # usa menor caminho ponderado por 'weight'
        nxt = min(
            remaining,
            key=lambda v: nx.shortest_path_length(G, current, v, weight=weight)
        )
        route.append(nxt)
        remaining.discard(nxt)
        current = nxt
    return route

def _pair_cost(G: nx.Graph, a: int, b: int, weight: str) -> float:
    # custo do menor caminho entre a e b pelo peso escolhido
    return nx.shortest_path_length(G, a, b, weight=weight)

def two_opt(sequence: List[int], G: nx.Graph, weight: str = "distance_km") -> List[int]:
    """
    Otimiza a ordem dos nós (sequência) usando 2-opt.
    Mantém o primeiro nó fixo (depot) e permuta o restante.
    """
    if len(sequence) < 4:
        return sequence[:]

    best = sequence[:]
    improved = True

    # Mantém o depot fixo na posição 0
    while improved:
        improved = False
        # i começa em 1 para não mexer no depot
        for i in range(1, len(best) - 2):
            for k in range(i + 1, len(best) - 1):
                a, b = best[i - 1], best[i]
                c, d = best[k], best[k + 1]
                # custo atual das arestas (a-b) + (c-d)
                old_cost = _pair_cost(G, a, b, weight) + _pair_cost(G, c, d, weight)
                # custo novo (a-c) + (b-d) invertendo [i:k]
                new_cost = _pair_cost(G, a, c, weight) + _pair_cost(G, b, d, weight)
                if new_cost + 1e-9 < old_cost:
                    best[i : k + 1] = reversed(best[i : k + 1])
                    improved = True
    return best

def stitch_shortest_paths(G: nx.Graph, sequence: List[int], weight: str = "distance_km") -> Tuple[List[int], float]:
    full = []
    total = 0.0
    for a, b in zip(sequence[:-1], sequence[1:]):
        sp = nx.shortest_path(G, a, b, weight=weight)
        if full: sp = sp[1:]  # evita duplicar nó
        full += sp
        total += nx.path_weight(G, sp, weight=weight)
    return full, total
