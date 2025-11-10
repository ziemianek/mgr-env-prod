import glob
import matplotlib.pyplot as plt
import pandas as pd
import pathlib
import re
import sys

from collections import defaultdict
from typing import Dict, List
from scripts.utils.logger import *


# ===== START OF CONFIGURATION =====
TEST_TYPE = "stress"  # stress / soak
PATH = f"./data/*/{TEST_TYPE.lower()}*/*.csv"
RPS_PATH = f"./data/*/mean_rps_{TEST_TYPE.lower()}.csv"
PLOT_OUTPUT_PATH = f"./results/http_latency_{TEST_TYPE.lower()}_plot.png"
DF_OUTPUT_PATH = "./data/{}/http_latency_{}.csv"
# ===== END OF CONFIGURATION =====

REQUIRED_FILES = [
    "95th Percentile Latency (ms).csv",
    "Average Request Duration (ms).csv",
    f"mean_rps_{TEST_TYPE.lower()}.csv"
]


def get_data_from_path(path: str, read_func: callable = pd.read_csv) -> Dict[str, pd.DataFrame]:
    data = {}
    for file in glob.glob(path):
        if file.strip().split("/")[-1] in REQUIRED_FILES:
            print_debug(f"Found file matching pattern: {file}")
            data[file] = read_func(file)
    if len(data) == 0:
        print_error("Did not found any data! Returning empty dict")
    else:
        print_debug(f"Found {len(data)} files total")
    return data


def save_df_to_csv(path: str, df: pd.DataFrame) -> None:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=True, encoding="utf-8")
    print_debug(f"Saved df to {path}")


def get_cluster_name(path: str) -> str:
    m = re.search(r'(aks|gke|eks)', path.lower())
    cluster = m.group(1) if m else "unknown"
    if not cluster == "unknown":
        print_debug(f"Found cluster name: \"{m.group(1)}\" in \"{path}\"")
    else:
        print_error(f"Could not find cluster name in \"{path}\"")
    return cluster


def mean_metric_per_cluster(data: dict[str, pd.DataFrame], metric: str) -> dict[str, pd.DataFrame]:
    clusters = defaultdict(list)
    result = {}
    for p, df in data.items():
        if metric in df.columns:
            print_debug(f"Found metric: \"{metric}\" in {p}")
            cluster = get_cluster_name(p)
            clusters[cluster].append(df[['relative_time_min', metric]].copy())
        else:
            print_debug(f"metric: \"{metric}\" not found in {p}. Skipping...")
    for cluster, dfs in clusters.items():
        combined = pd.concat(dfs, ignore_index=True)
        mean_df = (
            combined.groupby('relative_time_min', as_index=False)[metric]
                    .mean()
                    .rename(columns={metric: f'mean {metric}'})
        )
        result[cluster] = mean_df
    return result


def dry_run() -> bool:
    if len(sys.argv) == 1:
        return False
    return sys.argv[1] == "--dry-run"


def combine_all(avg_dict, p95_dict, rps_dict):
    result = {}
    for cluster in avg_dict.keys():
        df_avg = avg_dict[cluster]
        df_p95 = p95_dict[cluster]
        df_rps = rps_dict[cluster]
        merged = (
            df_avg
            .merge(df_p95, on="relative_time_min", suffixes=("_avg", "_p95"))
            .merge(df_rps, on="relative_time_min")
        )
        result[cluster] = merged
    return result


def plot(data: Dict[str, pd.DataFrame]) -> None:
    clusters = list(data.keys())
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax, cluster in zip(axes, clusters):
        df = data[cluster]
        df.fillna(0, inplace=True)
        ax.plot(
            df["relative_time_min"],
            df["mean avg duration (ms)"],
            label="AVG (ms)",
            linewidth=2
        )
        ax.plot(
            df["relative_time_min"],
            df["mean p95 latency (ms)"],
            label="P95 (ms)",
            linewidth=2
        )
        ax.set_title(cluster.upper())
        ax.set_xlabel("Time (min)")
        ax.set_ylabel("Latency (ms)")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax2 = ax.twinx()
        ax2.plot(
            df["relative_time_min"],
            df["rps"],
            label="RPS",
            linewidth=2,
            linestyle="dashed",
            color="green",
            alpha=0.4
        )
        ax2.set_ylabel("RPS")
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines + lines2, labels + labels2, loc="upper left")
    plt.suptitle("Latency (AVG, P95) + RPS Over Time per Cluster", fontsize=14)
    plt.tight_layout()
    if not dry_run():
        plt.savefig(PLOT_OUTPUT_PATH, dpi=200)
    plt.show()


def main():
    data = get_data_from_path(PATH)
    rps = get_data_from_path(RPS_PATH)
    for p, df in data.items():
        print_debug(f"{p} -> shape {df.shape}")
        print_debug(f"Head of {p}:\n{df.head()}")
    avg = mean_metric_per_cluster(data, metric="avg duration (ms)")
    p95 = mean_metric_per_cluster(data, metric="p95 latency (ms)")
    rps_new = {}
    for p, df in rps.items():
        print_debug(f"{p} -> shape {df.shape}")
        print_debug(f"Head of {p}:\n{df.head()}")
        cluster = get_cluster_name(p)
        rps_new[cluster] = df
    for c, df in avg.items():
        print_debug(f"{c} ->\n{df.head()}")
    for c, df in p95.items():
        print_debug(f"{c} ->\n{df.head()}")
    combined = combine_all(avg, p95, rps_new)
    plot(combined)
    if not dry_run():
        for c, df in combined.items():
            save_df_to_csv(DF_OUTPUT_PATH.format(c, TEST_TYPE.lower()), df)


if __name__ == "__main__":
    main()