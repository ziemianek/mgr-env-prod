import glob
import matplotlib.pyplot as plt
import pandas as pd
import re
import sys

from collections import defaultdict
from typing import Dict, Tuple

from scripts.utils.logger import *
from scripts.utils.t0 import *


# ===== START OF CONFIGURATION =====
# TEST_TYPE = "stress"  # stress / soak
TEST_TYPE = "soak"
# TEST_START_FINISH = {"start": 0.0, "finish": 10.0}
# T0_MAP = STRESS_T0_MAP
T0_MAP = SOAK_T0_MAP
TEST_START_FINISH = {"start": 0.0, "finish": 240.0}
PATH = f"./data/*/{TEST_TYPE.lower()}*/kubelet_running_pods.csv"
PLOT_OUTPUT_PATH = f"./results/kubelet_running_pods_{TEST_TYPE.lower()}_plot.png"
# ===== END OF CONFIGURATION =====

cluster_colors = {
    "aks": "blue",
    "gke": "green",
    "eks": "orange"
}

def get_data_from_path(path: str, read_func: callable = pd.read_csv) -> Dict[str, pd.DataFrame]:
    data = {}
    for file in glob.glob(path):
        print_debug(f"Reading data from file \"{file}\"...")
        data[file] = read_func(file)
    if len(data) == 0:
        print_error("Did not found any data! Returning empty dict")
    else:
        print_debug(f"Found {len(data)} files total")
    return data


def dry_run() -> bool:
    if len(sys.argv) == 1:
        return False
    return sys.argv[1] == "--dry-run"


def get_cluster_name(path: str) -> str:
    m = re.search(r'(aks|gke|eks)', path.lower())
    cluster = m.group(1) if m else "unknown"
    if not cluster == "unknown":
        print_debug(f"Found cluster name: \"{m.group(1)}\" in \"{path}\"")
    else:
        print_error(f"Could not find cluster name in \"{path}\"")
    return cluster


def go_back_in_time(df: pd.DataFrame, hours: int) -> pd.DataFrame:
    df["Time"] = pd.to_datetime(df["Time"]) - pd.Timedelta(hours=hours)
    df["timestamp"] = df["timestamp"] - (hours * 60 * 60)
    df["relative_time_sec"] = df["relative_time_sec"] - (hours * 60 * 60)
    df["relative_time_min"] = df["relative_time_min"] - (hours * 60)
    return df


def fix_duplicate_time(p: str, df: pd.DataFrame, t0: Dict[str, pd.Timestamp]) -> pd.DataFrame:
    key = "_".join(p.split("/")[2:4])
    print_debug(f"Key for t0: {key}")
    df["Time"] = pd.to_datetime(df["Time"])
    mask = df["Time"].diff().dt.total_seconds() == 0
    df.loc[mask, "Time"] = df.loc[mask, "Time"] + pd.Timedelta(seconds=30)
    df["timestamp"] = df["Time"].astype("int64") // 1_000_000_000
    df["relative_time_sec"] = df["timestamp"] - t0[key].timestamp()
    df["relative_time_min"] = df["relative_time_sec"] / 60.0
    return df


def clip_data_to_timeframe(df: pd.DataFrame, col: str, range: Tuple[int, int]) -> pd.DataFrame:
    return df[df[col].between(range[0], range[1])]


def calc_mean_per_cluster(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    clusters = defaultdict(list)
    result = {}
    for p, df in data.items():
        node_cols = [c for c in df.columns if c.startswith("node")]
        if not node_cols:
            print_error(f"No node cols with prefix 'node' in {p}, skipping")
            continue
        print_debug(f"Found node columns {node_cols} in {p}")
        cluster = get_cluster_name(p)
        tmp = df[['relative_time_min'] + node_cols].copy()
        clusters[cluster].append(tmp)
    for cluster, dfs in clusters.items():
        combined = pd.concat(dfs, ignore_index=True)
        mean_df = (
            combined
            .groupby("relative_time_min", as_index=False)
            [node_cols]
            .mean()
        )
        for c in node_cols:
            mean_df[f"mean {c}"] = (
                mean_df[c]
                .round()
                .astype("Int64")
            )
            mean_df = mean_df.drop(columns=[c])
        result[cluster] = mean_df
    return result


def plot(data: Dict[str, pd.DataFrame]) -> None:
    plt.figure(figsize=(12, 6))
    for cluster, df in data.items():
        print_debug(f"From inside plot function: {cluster} -> {df.shape}")
        print_debug(f"From inside plot function: {df.columns}")
        color = cluster_colors[cluster]
        if "mean node1" in df.columns:
            plt.plot(
                df["relative_time_min"],
                df["mean node1"],
                linewidth=2,
                color=color,
                label=f"{cluster.upper()} Węzeł 1"
            )
        if "mean node2" in df.columns:
            plt.plot(
                df["relative_time_min"],
                df["mean node2"],
                linewidth=2,
                color=color,
                linestyle="dashed",
                alpha=0.7,
                label=f"{cluster.upper()} Węzeł 2"
            )
    plt.axvline(x=TEST_START_FINISH["start"], color="red", linestyle="--", linewidth=1)
    plt.axvline(x=TEST_START_FINISH["finish"], color="red", linestyle="--", linewidth=1)
    plt.axvspan(TEST_START_FINISH["start"], TEST_START_FINISH["finish"], color="grey", alpha=0.1)
    plt.title("Średnia liczba podów na węzeł w klastrach")
    plt.xlabel("Czas od rozpoczęcia testu (min)")
    plt.ylabel("Średnia liczba podów")
    plt.yticks(range(0, 51, 5))
    plt.xticks(range(0, 271, 30))
    plt.grid(True, linestyle="--", alpha=0.4)
    # plt.legend(loc="upper left")
    plt.legend(loc="lower right")
    plt.tight_layout()
    if not dry_run():
        plt.savefig(PLOT_OUTPUT_PATH, dpi=200)
    else:
        plt.show()


def main():
    data = get_data_from_path(PATH)
    for p, df in data.items():
        if "aks" in p:
            df = go_back_in_time(df, 1)
        if "eks" in p:
            df = go_back_in_time(df, 1)
        if "gke" in p:    
            df = go_back_in_time(df, 2)
        df = fix_duplicate_time(p, df, T0_MAP)
        df = clip_data_to_timeframe(df, "relative_time_min", (0, 260))
        data[p] = df
    for p, df in data.items():
        print_debug(f"{p} has shape (rows, cols) -> {df.shape}")
        print_debug(df)
    res = calc_mean_per_cluster(data)
    for _, df in res.items():
        print_debug(f"Pods head: {df.head(15)}")
    plot(res)


if __name__ == "__main__":
    main()
