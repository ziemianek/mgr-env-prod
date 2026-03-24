import glob
import matplotlib.pyplot as plt
import pandas as pd
import re
import sys

from typing import Dict
from scripts.utils.logger import *


# ===== START OF CONFIGURATION =====
# TEST_TYPE = "stress"
TEST_TYPE = "soak"
# TEST_START_FINISH = {"start": 0.0, "finish": 10.0}
TEST_START_FINISH = {"start": 0.0, "finish": 240.0}
PATH = f"./data/*/{TEST_TYPE.lower()}_node_merged_df.csv"
CPU_PLOT_OUTPUT_PATH = f"./results/cpu_{TEST_TYPE.lower()}_plot.png"
MEM_PLOT_OUTPUT_PATH = f"./results/mem_{TEST_TYPE.lower()}_plot.png"
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


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    cpu_cols = [c for c in df.columns if "CPU_Utilisation" in c]
    node_cpu_groups = {}
    for col in cpu_cols:
        m = re.search(r"node(\d+)_CPU_Utilisation", col)
        if m:
            node = f"node{m.group(1)}"
            node_cpu_groups.setdefault(node, []).append(col)
    summary_df = pd.DataFrame({"relative_time_min": df["relative_time_min"]})
    for node, cols in node_cpu_groups.items():
        numeric = df[cols].replace('%','', regex=True).astype(float)
        summary_df[f"{node}_cpu_avg"] = numeric.mean(axis=1)
    mem_cols = [c for c in df.columns if "Memory_Utilisation" in c]
    mem_groups = {}
    for col in mem_cols:
        m = re.search(r"node(\d+)_Memory_Utilisation", col)
        if m:
            node = f"node{m.group(1)}"
            mem_groups.setdefault(node, []).append(col)
    for node, cols in mem_groups.items():
        numeric = df[cols].replace('%', '', regex=True).astype(float)
        summary_df[f"{node}_mem_avg"] = numeric.mean(axis=1)
    return summary_df


def get_cluster_name(path: str) -> str:
    m = re.search(r'(aks|gke|eks)', path.lower())
    cluster = m.group(1) if m else "unknown"
    if not cluster == "unknown":
        print_debug(f"Found cluster name: \"{m.group(1)}\" in \"{path}\"")
    else:
        print_error(f"Could not find cluster name in \"{path}\"")
    return cluster


def plot_cpu(data: Dict[str, pd.DataFrame]) -> None:
    plt.figure(figsize=(12, 6))
    for cluster, df in data.items():
        color = cluster_colors[cluster]
        if "node1_cpu_avg" in df.columns:
            plt.plot(
                df["relative_time_min"],
                df["node1_cpu_avg"],
                linewidth=2,
                color=color,
                label=f"{cluster.upper()} Węzeł 1"
            )
        if "node2_cpu_avg" in df.columns:
            plt.plot(
                df["relative_time_min"],
                df["node2_cpu_avg"],
                linewidth=2,
                color=color,
                linestyle="dashed",
                alpha=0.7,
                label=f"{cluster.upper()} Węzeł 2"
            )
    plt.axvline(x=TEST_START_FINISH["start"], color="red", linestyle="--", linewidth=1)
    plt.axvline(x=TEST_START_FINISH["finish"], color="red", linestyle="--", linewidth=1)
    plt.axvspan(TEST_START_FINISH["start"], TEST_START_FINISH["finish"], color="grey", alpha=0.1)
    plt.xlabel("Czas od rozpoczęcia testu (min)")
    plt.ylabel("Zużycie CPU (%)")
    plt.yticks(range(0, 101, 10))
    plt.xticks(range(0, 271, 30))
    plt.title("Porównanie zużycia CPU między klastrami")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc="upper left")
    plt.tight_layout()
    if not dry_run():
        plt.savefig(CPU_PLOT_OUTPUT_PATH, dpi=200)
    # plt.show()


def plot_mem(data: Dict[str, pd.DataFrame]) -> None:
    plt.figure(figsize=(12, 6))
    for cluster, df in data.items():
        color = cluster_colors[cluster]
        if "node1_mem_avg" in df.columns:
            plt.plot(
                df["relative_time_min"],
                df["node1_mem_avg"],
                linewidth=2,
                color=color,
                label=f"{cluster.upper()} Węzeł 1"
            )
        if "node2_mem_avg" in df.columns:
            plt.plot(
                df["relative_time_min"],
                df["node2_mem_avg"],
                linewidth=2,
                color=color,
                linestyle="dashed",
                alpha=0.7,
                label=f"{cluster.upper()} Węzeł 2"
            )
    plt.axvline(x=TEST_START_FINISH["start"], color="red", linestyle="--", linewidth=1)
    plt.axvline(x=TEST_START_FINISH["finish"], color="red", linestyle="--", linewidth=1)
    plt.axvspan(TEST_START_FINISH["start"], TEST_START_FINISH["finish"], color="grey", alpha=0.1)
    plt.xlabel("Czas od rozpoczęcia testu (min)")
    plt.ylabel("Zużycie RAM (%)")
    plt.yticks(range(0, 31, 5))
    plt.xticks(range(0, 271, 30))
    plt.title("Porównanie zużycia RAM między klastrami")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc="upper left")
    plt.tight_layout()
    if not dry_run():
        plt.savefig(MEM_PLOT_OUTPUT_PATH, dpi=200)
    # plt.show()


def main():
    data = get_data_from_path(PATH)
    data_fmt = {}
    for p, df in data.items():
        c = get_cluster_name(p)
        data_fmt[c] = summarize(df)
    plot_cpu(data_fmt)
    plot_mem(data_fmt)


if __name__ == "__main__":
    main()
