#!/usr/bin/env python3
import sys
import pandas as pd
from collections import defaultdict
from pathlib import Path

from scripts.utils.logger import *


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    first_col = df.columns[0]
    df = df.rename(columns={first_col: "test"})
    df["cluster"] = df["test"].str.split("-").str[0]
    return df


def sum_requests_per_cluster(csv_paths):
    totals = defaultdict(float)
    for path in csv_paths:
        df = load_csv(path)
        if "http_reqs_total" not in df.columns:
            raise ValueError(f"No column http_reqs_total in file {path}")
        grouped = df.groupby("cluster")["http_reqs_total"].sum()
        for cluster, total in grouped.items():
            totals[cluster] += total
    return totals


def compute_cost_per_mln(totals, cost_map):
    result = {}
    for cluster, total_reqs in totals.items():
        cost = cost_map.get(cluster)
        if cost is None:
            result[cluster] = None
            continue
        cost_per_1000 = cost / (total_reqs / 1_000_000.0)
        result[cluster] = cost_per_1000
    return result


def main():
    CLUSTER_COSTS = {
        "aks": 25.71,
        "eks": 24.37,
        "gke": 47.73,
    }
    csv_paths = [
        "data/k6_soak_results_summary.csv",
        "data/k6_stress_results_summary.csv"
    ]
    for p in csv_paths:
        if not Path(p).is_file():
            print_error(f"File not found: {p}")
            sys.exit(1)
    totals = sum_requests_per_cluster(csv_paths)
    print_debug("Sums:")
    for cluster in sorted(totals.keys()):
        print_debug(f"  - {cluster.upper()}: {int(totals[cluster]):,} requests".replace(",", " "))
    print_debug("Costs:")
    costs = compute_cost_per_mln(totals, CLUSTER_COSTS)
    for cluster, cost in costs.items():
        print_debug(f"{cluster.upper():4} -> {cost:.6f} zł / 1 mln reqs")


if __name__ == "__main__":
    main()
