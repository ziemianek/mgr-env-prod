#!/usr/bin/env python3

import glob
import pandas as pd
import pathlib

from typing import Dict
from logger import *


# === CONFIGURATION ===
TEST_TYPE = "stress"
# TEST_TYPE = "soak"
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


def save_df_to_csv(path: str, df: pd.DataFrame) -> None:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False, encoding="utf-8")
    print_debug(f"Saved df to {path}")


def resample(df: pd.DataFrame, interval_s: int = 30) -> pd.DataFrame:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index('timestamp')
    return df.resample(f"{interval_s}s").mean().interpolate(method="linear")


def main():
    data = get_data_from_path(f"./data/*/{TEST_TYPE.lower()}*/*.csv")
    for p, df in data.items():
        print(df.head())
        df = resample(df)
        print(df.head())
        break


if __name__ == "__main__":
    main()
