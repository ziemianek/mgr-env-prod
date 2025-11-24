import pandas as pd
import pathlib
import sys

from collections import defaultdict
from typing import Dict
from scripts.utils.logger import *


CLUSTERS = ["aks", "eks", "gke"]
TEST_TYPE = "soak"
# TEST_TYPE = "stress"


def get_data_from_path(path: str) -> pd.DataFrame:
    path = pathlib.Path(path)
    if not path.exists():
        print_error(f"File \"{path}\" not found")
        sys.exit(1)
    print_debug(f"Reading data from file \"{path}\"...")
    return pd.read_csv(path)


def mean_of_col(df: pd.DataFrame, col: str, dec_acc: int = 2) -> float:
    return round(df.loc[:, col].mean(), dec_acc)


def percent_to_float(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    s = s.str.replace("%", "", regex=False)
    return s.astype(float)


def mean_of_multiple_cols(df: pd.DataFrame, metric: str, dec_acc: int = 2) -> float:
    vals = []
    for col in df.columns:
        if metric.lower().strip() in col.lower().strip():
            df[col] = percent_to_float(df[col])
            vals.append(mean_of_col(df, col, dec_acc))
    return round(sum(vals) / len(vals), dec_acc)


def pprint_data(data: Dict[str, Dict[str, float]]) -> None:
    headers = [
        "Platforma", 
        "Średnie RPS", 
        "Średni czas odp. (s)", 
        "P95 czas odp. (s)", 
        "Średnie CPU (%)", 
        "Średnie RAM (%)"
    ]
    print(f"{headers[0]:<10} | {headers[1]:<12} | {headers[2]:<20} | {headers[3]:<18} | {headers[4]:<15} | {headers[5]:<15}")
    print("-" * 100)
    for platform, metrics in data.items():
        print(
            f"{platform.upper():<10} | "
            f"{metrics['rps']:<12.2f} | "
            f"{metrics['latency']:<20.2f} | "
            f"{metrics['p95_latency']:<18.2f} | "
            f"{metrics['cpu_usage']:<15.2f} | "
            f"{metrics['ram_usage']:<15.2f}"
        )


def main():
    data = defaultdict(dict)
    for c in CLUSTERS:
        # calculate mean rps
        df = get_data_from_path(f"data/{c}/mean_rps_{TEST_TYPE.lower()}.csv")
        data[c].update({"rps": mean_of_col(df, "rps", 0)})

        # calculate mean latency/p95 latency
        df = get_data_from_path(f"data/{c}/http_latency_{TEST_TYPE.lower()}.csv")
        data[c].update({"latency": mean_of_col(df, "mean avg duration (ms)") / 60})
        data[c].update({"p95_latency": mean_of_col(df, "mean p95 latency (ms)") / 60})

        # calculate mean of CPU/RAM usage
        df = get_data_from_path(f"./data/{c}/{TEST_TYPE.lower()}_node_merged_df.csv")
        data[c].update({"cpu_usage": mean_of_multiple_cols(df, "CPU")})
        data[c].update({"ram_usage": mean_of_multiple_cols(df, "Memory")})

    pprint_data(data)


if __name__ == "__main__":
    main()