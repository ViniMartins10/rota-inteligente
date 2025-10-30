# src/main.py
"""
Pipeline com 2-opt opcional + escolha de peso (distance_km ou time_h)
Gera comparativo Antes vs Depois (km, tempo, custo).
"""
import argparse
import pandas as pd
import networkx as nx
from pathlib import Path

from src.graph_utils import load_city_graph
from src.clustering import kmeans_cluster_deliveries
from src.routing import nearest_neighbor_tsp, stitch_shortest_paths, two_opt
from src.visualize import plot_route
from src.evaluate import evaluate_route


def run(k_drivers: int, base_path: str = ".", weight: str = "time_h", use_2opt: bool = True):
    base = Path(base_path)
    (base / "outputs").mkdir(parents=True, exist_ok=True)

    G = load_city_graph(base / "data" / "nodes.csv", base / "data" / "edges.csv")
    nodes_df = pd.read_csv(base / "data" / "nodes.csv")
    deliveries_df = pd.read_csv(base / "data" / "deliveries.csv")
    deliveries_df["node_id"] = deliveries_df["node_id"].astype(int)

    clustered, _ = kmeans_cluster_deliveries(nodes_df, deliveries_df, k=k_drivers)
    depot = 0  # "Centro"

    results = []
    comp_rows = []

    print(f"\n=== Executando com peso: '{weight}' | 2-opt: {'ON' if use_2opt else 'OFF'} ===\n")

    for cluster_id in sorted(clustered["cluster"].unique()):
        d_cluster = clustered[clustered["cluster"] == cluster_id]
        targets = d_cluster["node_id"].tolist()
        if not targets:
            continue

        # Sequência inicial (Nearest Neighbor)
        seq0 = nearest_neighbor_tsp(G, nodes=targets, start=targets[0], weight=weight)
        seq0 = [depot] + seq0

        # BEFORE
        full0, _ = stitch_shortest_paths(G, seq0, weight=weight)
        met0 = evaluate_route(G, full0)
        fig0 = plot_route(G, full0, title=f"Rota cluster {cluster_id} — BEFORE")
        fig0.savefig(base / "outputs" / f"rota_cluster_{cluster_id}_before.png")

        # AFTER (com ou sem 2-opt)
        if use_2opt:
            from copy import deepcopy
            seq1 = two_opt(deepcopy(seq0), G, weight=weight)
        else:
            seq1 = seq0[:]

        full1, _ = stitch_shortest_paths(G, seq1, weight=weight)
        met1 = evaluate_route(G, full1)
        fig1 = plot_route(G, full1, title=f"Rota cluster {cluster_id} — AFTER")
        fig1.savefig(base / "outputs" / f"rota_cluster_{cluster_id}_after.png")

        results.append({"cluster": int(cluster_id), "sequence": seq1, **met1})

        comp_rows.append({
            "cluster": int(cluster_id),
            "weight": weight,
            "km_before": round(met0["distance_km"], 3),
            "km_after": round(met1["distance_km"], 3),
            "time_h_before": round(met0["time_h"], 4),
            "time_h_after": round(met1["time_h"], 4),
            "fuel_brl_before": round(met0["fuel_cost_brl"], 2),
            "fuel_brl_after": round(met1["fuel_cost_brl"], 2),
            "improv_km_%": round(100.0 * (met0["distance_km"] - met1["distance_km"]) / met0["distance_km"], 2) if met0["distance_km"] > 0 else 0.0,
            "improv_time_%": round(100.0 * (met0["time_h"] - met1["time_h"]) / met0["time_h"], 2) if met0["time_h"] > 0 else 0.0,
            "improv_cost_%": round(100.0 * (met0["fuel_cost_brl"] - met1["fuel_cost_brl"]) / met0["fuel_cost_brl"], 2) if met0["fuel_cost_brl"] > 0 else 0.0,
        })

    # Salvar resultados
    out = pd.DataFrame(results)
    out.to_csv(base / "outputs" / "resumo_rotas.csv", index=False)
    comp = pd.DataFrame(comp_rows)
    comp.to_csv(base / "outputs" / "rotas_comparativo.csv", index=False)

    print("\n=== COMPARATIVO FINAL ===")
    if not comp.empty:
        print(comp.to_string(index=False))
        print(f"\nGanho médio (tempo): {comp['improv_time_%'].mean():.2f}%")
        print(f"Ganho médio (km): {comp['improv_km_%'].mean():.2f}%")
        print(f"Ganho médio (custo): {comp['improv_cost_%'].mean():.2f}%")
    else:
        print("Sem dados de comparativo.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Otimização de rotas com K-Means + 2-opt")
    ap.add_argument("--drivers", "-k", type=int, default=2, help="Número de entregadores (clusters)")
    ap.add_argument("--base", type=str, default=".", help="Caminho da raiz do projeto")
    ap.add_argument("--weight", type=str, choices=["distance_km", "time_h"], default="time_h", help="Peso da otimização (distance_km ou time_h)")
    ap.add_argument("--no-2opt", action="store_true", help="Desativa a otimização 2-opt")
    args = ap.parse_args()

    run(args.drivers, args.base, weight=args.weight, use_2opt=not args.no_2opt)
