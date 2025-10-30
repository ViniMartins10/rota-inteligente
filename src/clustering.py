
import pandas as pd
from sklearn.cluster import KMeans

def kmeans_cluster_deliveries(nodes_df: pd.DataFrame, deliveries_df: pd.DataFrame, k: int):
    # Merge node coords into deliveries
    merged = deliveries_df.merge(nodes_df[["id","x","y"]], left_on="node_id", right_on="id", how="left")
    X = merged[["x", "y"]].values
    model = KMeans(n_clusters=k, n_init="auto", random_state=42)
    labels = model.fit_predict(X)
    merged["cluster"] = labels
    return merged, model
