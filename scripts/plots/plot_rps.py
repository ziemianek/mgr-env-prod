#!/usr/bin/env python3

import glob
import matplotlib.pyplot as plt
import pathlib
import pandas as pd
import re
import sys

from collections import defaultdict
from typing import Dict
from scripts.utils.logger import *
from scripts.utils.t0 import *


# ===== START OF CONFIGURATION =====
TEST_TYPE = "stress"  # stress / soak
PATH = f"./data/*/{TEST_TYPE.lower()}*/Total Requests (increase over 1m).csv"
OUTPUT_PATH = f"rps_{TEST_TYPE.lower()}_plot.png"
# ===== END OF CONFIGURATION =====


def get_data_from_path(path: str, read_func: callable = pd.read_csv) -> Dict[str, pd.DataFrame]:
    data = {}
    for file in glob.glob(path):
        data[file] = read_func(file)
    print_debug(f"Found {len(data)} files")
    return data


def save_df_to_csv(path: str, df: pd.DataFrame) -> None:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=True, encoding="utf-8")
    print_debug(f"Saved df to {path}")


def add_rps(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df["rps"] = df["mean_requests"] / 60.0
        print_debug("Added RPS column to dataframe")
        return df
    except Exception as e:
        print_error(f"Error while adding RPS: {e}")


def get_cluster_name(path: str) -> str:
    m = re.search(r'(aks|gke|eks)', path.lower())
    cluster = m.group(1) if m else "unknown"
    if not cluster == "unknown":
        print_debug(f"Found cluster name: \"{m.group(1)}\" in \"{path}\"")
    else:
        print_error(f"Could not find cluster name in \"{path}\"")
    return cluster


# NOTE: this was AI generated
def mean_requests_per_cluster(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    clusters = defaultdict(list)
    result = {}
    for p, df in data.items():
        cluster = get_cluster_name(p)
        clusters[cluster].append(df[['relative_time_min', 'requests']].copy())
    for cluster, dfs in clusters.items():
        combined = pd.concat(dfs, ignore_index=True)
        mean_df = (
            combined.groupby('relative_time_min', as_index=False)['requests']
                    .mean()
                    .rename(columns={'requests': 'mean_requests'})
        )
        result[cluster] = mean_df
    return result


def dry_run() -> bool:
    if len(sys.argv) == 1:
        return False
    return sys.argv[1] == "--dry-run"


def plot(data: Dict[str, pd.DataFrame]) -> None:
    plt.figure(figsize=(12, 6))

    for cluster, df in data.items():
        plt.plot(
            df["relative_time_min"],
            df["rps"],
            label=cluster.upper(),
            linewidth=2
        )

    plt.xlabel("Czas od rozpoczęcia testu (min)")
    plt.ylabel("Żadania/sekunda")
    plt.title("RPS over Time per Cluster")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()
    if not dry_run():
        plt.savefig(OUTPUT_PATH, dpi=200)


def main() -> None:
    if dry_run():
        print_debug("=== DRY RUN ===")
    data = get_data_from_path(PATH)
    for p, df in data.items():
        print_debug(f"{p} -> shape {df.shape}")
        print_debug(f"Head:\n{df.head()}")
    res = mean_requests_per_cluster(data)
    for c, df in res.items():
        df = add_rps(df)
        print_debug(f"{c} -> shape {df.shape}")
        print_debug(f"Head of {c}:\n{df.head()}")
    plot(res)


if __name__ == "__main__":
    main()
