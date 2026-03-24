#!/usr/bin/env python3

import glob
import matplotlib.pyplot as plt
import pathlib
import pandas as pd
import re
import sys

from collections import defaultdict
from typing import Dict, Tuple
from scripts.utils.logger import *
from scripts.utils.t0 import *


# ===== START OF CONFIGURATION =====
TEST_TYPE = "stress"  # stress / soak
TEST_START_FINISH = {"start": 0.0, "finish": 10.0}
# TEST_TYPE = "soak"
# TEST_START_FINISH = {"start": 0.0, "finish": 240.0}
PATH = f"./data/*/{TEST_TYPE.lower()}*/Total Requests (increase over 1m).csv"
PLOT_OUTPUT_PATH = f"./results/mean_rps_{TEST_TYPE.lower()}_plot.png"
DF_OUTPUT_PATH = "./data/{}/mean_rps_{}.csv"
# ===== END OF CONFIGURATION =====

cluster_colors = {
    "aks": "blue",
    "gke": "green",
    "eks": "orange"
}


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
        # because of misconfiguration of istio_requests_total metric
        # got double the amount of requests going through istio IGW
        # reporter=source       -> +1
        # reporter=destination  -> +1
        # because of that, rps have to be divided by 2
        df["rps"] = df["rps"] / 2
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


def clip_data_to_timeframe(df: pd.DataFrame, col: str, range: Tuple[int, int]) -> pd.DataFrame:
    return df[df[col].between(range[0], range[1])]


def sum_requests(data: Dict[str, pd.DataFrame]) -> Dict[str, int]:
    cluster_totals = defaultdict(int)
    for path, df in data.items():
        cluster = get_cluster_name(path)
        if "requests" not in df.columns:
            print_error(f"Missing columns 'requests' in file: {path}")
            continue
        try:
            total = df["requests"].sum()
            cluster_totals[cluster] += total
            print_debug(f"{cluster.upper()} -> {total} requests (from {path})")
        except Exception as e:
            print_error(f"Couldnt calculate sum from {path}: {e}")
    return dict(cluster_totals)


def plot(data: Dict[str, pd.DataFrame]) -> None:
    plt.figure(figsize=(12, 6))
    for cluster, df in data.items():
        df = clip_data_to_timeframe(df, "relative_time_min", (0, 13))
        color = cluster_colors[cluster]
        plt.plot(
            df["relative_time_min"],
            df["rps"],
            label=cluster.upper(),
            linewidth=2,
            color=color
        )
    plt.axvline(x=TEST_START_FINISH["start"], color="red", linestyle="--", linewidth=1)
    plt.axvline(x=TEST_START_FINISH["finish"], color="red", linestyle="--", linewidth=1)
    plt.axvspan(TEST_START_FINISH["start"], TEST_START_FINISH["finish"], color="grey", alpha=0.1)
    plt.title("Liczba żądań na sekundę w czasie dla poszczególnych klastrów")
    plt.xlabel("Czas od rozpoczęcia testu (min)")
    plt.ylabel("Żądania na sekunde")
    plt.yticks(range(0, 301, 50))
    plt.xticks(range(0, 13, 2))
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc="upper left")
    plt.tight_layout()
    if not dry_run():
        plt.savefig(PLOT_OUTPUT_PATH, dpi=200)
    else:
        plt.show()


def save_df_to_csv(path: str, df: pd.DataFrame) -> None:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False, encoding="utf-8")
    print_debug(f"Saved df to {path}")


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
        if not dry_run():
            save_df_to_csv(
                DF_OUTPUT_PATH.format(c, TEST_TYPE.lower()),
                df
            )
    plot(res)
    requests_summary = sum_requests(data)
    print_debug("=== TOTAL REQUESTS PER CLUSTER ===")
    for c, v in requests_summary.items():
        print_debug(f"{c.upper()}: {v:,} requests")


if __name__ == "__main__":
    main()
