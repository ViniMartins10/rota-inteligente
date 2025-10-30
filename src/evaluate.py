
from typing import Dict, List
import networkx as nx

FUEL_KM_PER_LITER = 35.0  # moto típica
COST_PER_LITER = 6.50     # BRL

def evaluate_route(G: nx.Graph, route_nodes: List[int]) -> Dict[str, float]:
    dist = nx.path_weight(G, route_nodes, weight="distance_km")
    time_h = nx.path_weight(G, route_nodes, weight="time_h")
    fuel_l = dist / FUEL_KM_PER_LITER
    fuel_cost = fuel_l * COST_PER_LITER
    return {"distance_km": dist, "time_h": time_h, "fuel_l": fuel_l, "fuel_cost_brl": fuel_cost}
