#!/usr/bin/env python3

import glob
import numpy as np
import pathlib
import pandas as pd
import re
import sys

from typing import Dict, Optional
from scripts.utils.logger import *


# ===== START OF CONFIGURATION =====
# TEST_TYPE = "stress"  # stress / soak
TEST_TYPE = "soak"
PATH = f"./data/*/{TEST_TYPE.lower()}*/k6_results.txt"
OUTPUT_PATH = f"./data/k6_{TEST_TYPE.lower()}_results_summary.csv"
# ====== END OF CONFIGURATION ======


def to_seconds(value: str) -> float:
    res = np.nan
    if not isinstance(value, str) or not value:
        return res
    value = value.strip()
    if value.endswith("ms"):
        res = float(value.replace("ms", "")) / 1000
    elif value.endswith("m"):
        res = float(value.replace("m", "")) * 60
    elif value.endswith("s"):
        res = float(value.replace("s", ""))
    else:
        print_debug(f"Time not found in {value}")
    return res


def to_megabytes(value: str) -> float:
    res = np.nan
    if not isinstance(value, str) or not value:
        return res
    value = value.replace("/s", "").strip()
    if not re.search(r"[\d\.]", value):
        return res
    if "GB" in value:
        res = float(re.sub(r"[^0-9.]", "", value)) * 1024
    if "MB" in value:
        res = float(re.sub(r"[^0-9.]", "", value))
    if "kB" in value:
        res = float(re.sub(r"[^0-9.]", "", value)) / 1024
    return res


def extract(pattern: str, text: str) -> Optional[str]:
    match = re.search(pattern, text)
    res = match.group(1).strip() if match else None
    if res is None:
        print_error(f"Could not extract metric from text based on pattern: \"{pattern}\", because there is no match.")
    else:
        print_debug(f"Found match for pattern: \"{pattern}\" in text")
    return res


def parse_k6_file(filepath: str) -> pd.DataFrame:
    print_debug(f"Parsing {filepath}...")
    data = {}
    p = pathlib.Path(filepath)
    text = p.read_text(encoding="utf-8", errors="ignore")
    cluster = p.parts[-3]  # 'aks' | 'eks' | 'gke'
    test = p.parts[-2]     # 'stress01', 'stress02', 'stress03'
    index = f"{cluster}-{test}"
    print_debug(f"Index for {filepath}: {index}")

    # HTTP
    data["http_req_duration_avg"] = to_seconds(extract(r"http_req_duration.*?avg=([\d\.a-z]+)", text))
    data["http_req_duration_med"] = to_seconds(extract(r"http_req_duration.*?med=([\d\.a-z]+)", text))
    data["http_req_duration_p90"] = to_seconds(extract(r"http_req_duration.*?p\(90\)=([\d\.a-z]+)", text))
    data["http_req_duration_p95"] = to_seconds(extract(r"http_req_duration.*?p\(95\)=([\d\.a-z]+)", text))
    data["http_req_duration_max"] = to_seconds(extract(r"http_req_duration.*?max=([\d\.a-z]+)", text))
    data["http_req_failed_%"] = float(extract(r"http_req_failed.*?([\d\.]+)%", text))
    data["http_reqs_total"] = float(extract(r"http_reqs\.*:\s+(\d+)", text))
    data["http_reqs_rate"] = float(extract(r"http_reqs.*?([\d\.]+)/s", text))

    # EXECUTION
    data["iteration_duration_avg"] = to_seconds(extract(r"iteration_duration.*?avg=([\d\.a-z]+)", text))
    data["iteration_duration_med"] = to_seconds(extract(r"iteration_duration.*?med=([\d\.a-z]+)", text))
    data["iteration_duration_p90"] = to_seconds(extract(r"iteration_duration.*?p\(90\)=([\d\.a-z]+)", text))
    data["iteration_duration_p95"] = to_seconds(extract(r"iteration_duration.*?p\(95\)=([\d\.a-z]+)", text))
    data["iterations_total"] = float(extract(r"iterations\.*:\s+(\d+)", text))
    data["iterations_rate"] = float(extract(r"iterations.*?([\d\.]+)/s", text))
    data["vus_max"] = float(extract(r"vus_max\.*:\s+(\d+)", text))
    data["vus"] = float(extract(r"vus\.*:\s+(\d+)", text))

    # NETWORK
    data["data_received_MB"] = to_megabytes(extract(r"data_received.*?:\s+([\d\.]+\s*[GMk]?B)", text))
    data["data_received_rate_MBps"] = to_megabytes(extract(r"data_received.*?\s+([\d\.]+\s*[GMk]?B/s)", text))
    data["data_sent_MB"] = to_megabytes(extract(r"data_sent.*?:\s+([\d\.]+\s*[GMk]?B)", text))
    data["data_sent_rate_MBps"] = to_megabytes(extract(r"data_sent.*?\s+([\d\.]+\s*[GMk]?B/s)", text))

    return pd.DataFrame([data], index=[index])


def get_data_from_path(path: str) -> Dict[str, pd.DataFrame]:
    data = {}
    for file in glob.glob(path):
        data[file] = parse_k6_file(file)
    print_debug(f"Found {len(data)} files")
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


def main() -> None:
    if dry_run():
        print_debug("=== DRY RUN ===")
    data = get_data_from_path(PATH)
    for k, df in data.items():
        print_debug(f"{k} -> shape {df.shape}")
    print_debug(f"Keys in dict: {list(data.keys())}")
    print_debug(f"Number of items in dict: {len(data)}")
    data_concat = pd.concat(data.values())
    print_debug(f"Generated DataFrame with summary: \n{data_concat.head(10)}")
    if not dry_run():
        save_df_to_csv(OUTPUT_PATH, data_concat)


if __name__ == "__main__":
    main()
