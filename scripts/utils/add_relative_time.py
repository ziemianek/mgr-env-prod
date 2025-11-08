#!/usr/bin/env python3

import glob
import pandas as pd
import pathlib

from typing import Dict

from logger import *
from t0 import *


# === CONFIGURATION ===
TEST_TYPE = "stress"
T0_MAP = STRESS_T0_MAP
# TEST_TYPE = "soak"
# T0_MAP = SOAK_T0_MAP
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


def is_timestamp(df: pd.DataFrame, column: str = "Time"):
    if not column in df.columns:
        raise KeyError(f"Column '{column}' is missing from the DataFrame")
    col = df[column]
    return pd.api.types.is_numeric_dtype(col)


def normalize_time(p: str, df: pd.DataFrame, column: str = "Time", utc: bool = True):
    try:
        if is_timestamp(df, column):
            df[column] = pd.to_datetime(df[column] / 1000, unit="s", utc=utc)
            print_debug(f"Normalized time in {p}")
    except KeyError as e:
        print_error(f"Could not normalize time in {p}: {e}")
    return df


def add_relative_time(path: str, df: pd.DataFrame) -> pd.DataFrame:
    if not "Time" in df.columns:
        raise KeyError("Column 'Time' is missing from the DataFrame")
    if not "timestamp" in df.columns:
        df = add_timestamp(df)
        print_debug(f"Added timestamp to \"{path}\"")
    if not "relative_time_sec" in df.columns:
        key = build_t0_key(path)
        df["relative_time_sec"] = df["timestamp"] - T0_MAP[key].timestamp()
        print_debug(f"Added relative time in seconds to \"{path}\"")
    if not "relative_time_min" in df.columns:
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
        df = normalize_time(p, df)
        try:
            data[p] = add_relative_time(p, df)
            save_df_to_csv(p, df)
        except KeyError as e:
            print_error(f"Could not add relative time to {p}: {e}")


if __name__ == "__main__":
    main()
