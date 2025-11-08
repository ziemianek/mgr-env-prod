#!/usr/bin/env python3

import glob
import pandas as pd
import pathlib

from typing import Dict
from logger import *

# === CONFIGURATION ===
TEST_TYPE = "stress"
T0_MAP = {
    # AKS
    "aks_stress01": pd.Timestamp("2025-10-26 14:15:30"),
    "aks_stress02": pd.Timestamp("2025-10-26 20:20:30"),
    "aks_stress03": pd.Timestamp("2025-10-17 07:17:30"),

    # # EKS
    # "eks_stress01": pd.Timestamp("2025-10-17 19:59:00"),
    # "eks_stress02": pd.Timestamp("2025-10-18 09:25:30"),
    # "eks_stress03": pd.Timestamp("2025-10-18 08:41:15"),

    # GKE
    "gke_stress01": pd.Timestamp("2025-10-17 20:09:30"),
    "gke_stress02": pd.Timestamp("2025-10-18 09:36:00"),
    "gke_stress03": pd.Timestamp("2025-10-18 08:51:00"),
}

# TEST_TYPE = "soak"
# T0_MAP = {
#     # AKS
#     "aks_soak01": pd.Timestamp("2025-10-26 13:29:30"),
#     "aks_soak02": pd.Timestamp("2025-10-26 06:36:00"),

#     # # EKS
#     # "eks_soak01": pd.Timestamp("2025-10-17 19:59:00"),
#     # "eks_soak02": pd.Timestamp("2025-10-18 09:25:30"),

#     # GKE
#     "gke_soak01": pd.Timestamp("2025-10-14 08:17:30"),
#     "gke_soak02": pd.Timestamp("2025-10-18 10:07:00"),
# }
# === END OF CONFIGURATION ===


def load_csv_to_dataframe(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        print_debug(f"Loaded data from \"{path}\"")
    except Exception as e:
        print_error(f"Failed loading data from \"{path}\": {e}")
    return df


def get_data_from_path(path: str) -> Dict[str, pd.DataFrame]:
    data = {}
    for file in glob.glob(path):
        data[file] = load_csv_to_dataframe(file)
    print_debug(f"Found {len(data)} files")
    return data


def add_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df["Time"] = pd.to_datetime(df["Time"])
        df["timestamp"] = df["Time"].astype('int64') // 10**9
        return df
    except Exception as e:
        print_error(f"Error while adding timestamp: {e}")


def build_t0_key(p: str) -> str:
    p = p.lower().split("/")
    provider = p[2]
    test = p[3]
    key = f"{provider}_{test}"
    print_debug(f"Created t0 key: {key}")
    return key


def add_relative_time(path: str, df: pd.DataFrame) -> pd.DataFrame:
    if not "Time" in df.columns:
        raise KeyError("Column 'Time' is missing from the DataFrame")
    df = add_timestamp(df)
    key = build_t0_key(path)
    df["relative_time_sec"] = df["timestamp"] - T0_MAP[key].timestamp()
    print_debug(f"Added relative time in seconds to \"{path}\"")
    df["relative_time_min"] = (df["relative_time_sec"] / 60)
    print_debug(f"Added relative time in minutes to \"{path}\"")
    return df


def save_df_to_csv(path: str, df: pd.DataFrame) -> None:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False, encoding="utf-8")
    print_debug(f"Saved df to {path}")


def main():
    for k, v in T0_MAP.items():
        print_debug(f"T0_MAP: {k}, {v}")
    data = get_data_from_path(f"./data/*/{TEST_TYPE.lower()}*/*.csv")
    for p, df in data.items():
        data[p] = add_relative_time(p, df)
        save_df_to_csv(p, df)
        break


if __name__ == "__main__":
    main()
