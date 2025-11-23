import glob
import os
import pandas as pd
import pathlib
import sys

from typing import Dict, Tuple
from scripts.utils.logger import *


# ===== START OF CONFIGURATION =====
# TEST_TYPE = "stress"
TEST_TYPE = "soak"
PATH = "./data/{}/{}*/node*/*.csv"
# ===== END OF CONFIGURATION =====

REQUIRED_FILES = [
    "CPU Utilisation.csv",
    "Memory Utilisation.csv",
    # "Network Utilisation.csv",
]


def get_data_from_path(path: str, read_func: callable = pd.read_csv) -> Dict[str, pd.DataFrame]:
    data = {}
    for file in glob.glob(path):
        if not file.split("/")[-1] in REQUIRED_FILES:
            print_debug(f"File \"{file}\" not in required files, skipping...")
        else:
            print_debug(f"Reading data from file \"{file}\"...")
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


def dry_run() -> bool:
    if len(sys.argv) == 1:
        return False
    return sys.argv[1] == "--dry-run"


def merge_dfs_per_cluster(cluster_name: str) -> pd.DataFrame:
    data = get_data_from_path(PATH.format(cluster_name, TEST_TYPE.lower()))
    combined = None
    for p, df in data.items():
        node = p.split("/")[-2]
        test = p.split("/")[-3]
        metric = os.path.basename(p).replace(".csv", "").replace(" ", "_")
        df = df.rename(
            columns=lambda c: f"{test}_{node}_{metric}_{c}" if not c in [
                "Time", "timestamp", "relative_time_sec", "relative_time_min"
            ] else c
        )
        df = df.drop(columns=["Time", "timestamp", "relative_time_sec"], errors="ignore")
        if combined is None:
            combined = df
        else:
            combined = pd.merge(combined, df, on="relative_time_min", how="outer")
    combined.sort_values("relative_time_min", inplace=True)
    return combined


def clip_data_to_timeframe(df: pd.DataFrame, col: str, range: Tuple[int, int]) -> pd.DataFrame:
    return df[df[col].between(range[0], range[1])]


def main():
    for cluster in ["aks", "eks", "gke"]:
        print_debug(f"Processing data for {cluster}...")
        df = merge_dfs_per_cluster(cluster)
        df = clip_data_to_timeframe(df, "relative_time_min", (0, 260))
        print(df.head())
        if not dry_run():
            save_df_to_csv(f"./data/{cluster}/{TEST_TYPE.lower()}_node_merged_df.csv", df)


if __name__ == "__main__":
    main()
