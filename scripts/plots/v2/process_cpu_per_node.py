#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from config import STRESS_T0_MAP

BASE_DIR = Path("data")
OUT_PATH = Path("results/cpu_avg_nodes_stress.png")
CLOUDS = ["aks", "eks", "gke"]
TESTS = ["stress01", "stress02", "stress03"]
DEBUG = True
RESAMPLE_INTERVAL = "30s"

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def debug(msg: str) -> None:
    if DEBUG:
        print(f"{datetime.datetime.now():%H:%M:%S} [DEBUG] {msg}")


def parse_percent(value: str) -> Optional[float]:
    try:
        if pd.isna(value):
            return None
        return float(str(value).strip().replace("%", "").replace(",", "."))
    except ValueError:
        return None


def load_cpu_node_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if not {"Time", "Utilisation"}.issubset(df.columns):
        raise ValueError(f"Nieoczekiwane kolumny w {path.name}: {df.columns.tolist()}")

    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    df["Utilisation"] = df["Utilisation"].apply(parse_percent)
    df = (
        df.dropna(subset=["Time", "Utilisation"])
        .sort_values("Time")
        .set_index("Time")
    )
    return df


def average_node_usage_for_cloud(cloud_dir: Path) -> Dict[str, pd.DataFrame]:
    cloud = cloud_dir.name
    debug(f"[{cloud.upper()}] Start analizy...")

    per_node_series: Dict[str, List[pd.DataFrame]] = {"node1": [], "node2": []}

    for test in TESTS:
        test_dir = cloud_dir / test
        if not test_dir.exists():
            debug(f"[{cloud}] ⚠️ Brak katalogu {test_dir}")
            continue

        t0_key = f"{cloud}_{test}"
        t0 = STRESS_T0_MAP.get(t0_key)
        if t0 is None:
            debug(f"[{cloud}/{test}] ❌ Brak wpisu T₀ w STRESS_T0_MAP")
            continue

        debug(f"[{cloud}/{test}] T₀ = {t0}")

        for node_dir in sorted(test_dir.glob("node*")):
            node_label = node_dir.name
            cpu_file = next(node_dir.glob("*CPU*.csv"), None)
            if cpu_file is None:
                debug(f"[{cloud}/{test}/{node_label}] ⚠️ Brak pliku CPU Utilisation")
                continue

            try:
                df = load_cpu_node_csv(cpu_file)
            except Exception as e:
                debug(f"[{cloud}/{test}/{node_label}] ❌ Błąd wczytywania: {e}")
                continue

            df = df.resample(RESAMPLE_INTERVAL).mean().interpolate("time")

            # Czas względny od T₀
            df["minutes_since_start"] = (df.index - t0).total_seconds() / 60.0
            df = df.set_index("minutes_since_start")
            per_node_series[node_label].append(df)

    avg_results: Dict[str, pd.DataFrame] = {}
    for node_label, dfs in per_node_series.items():
        if not dfs:
            debug(f"[{cloud}] ⚠️ Brak danych dla {node_label}")
            continue

        # znajdź wspólny zakres minut (nie dat)
        start = max(d.index.min() for d in dfs)
        end = min(d.index.max() for d in dfs)

        if start >= end:
            debug(f"[{cloud}] ⚠️ Brak wspólnego zakresu minut dla {node_label}")
            continue

        idx_grid = pd.RangeIndex(
            int(start * 60 // 30), int(end * 60 // 30) + 1
        ) * 0.5  # w minutach co 0.5 min

        # reindex + interpolacja
        aligned = [d.reindex(idx_grid, method=None).interpolate() for d in dfs]
        stacked = pd.concat([d["Utilisation"] for d in aligned], axis=1)
        avg = stacked.mean(axis=1)
        out = pd.DataFrame({"avg_utilisation": avg})
        avg_results[node_label] = out

        debug(f"[{cloud}] {node_label}: zapisano {len(out)} wierszy średnich")

    return avg_results


def plot_all_clouds(avg_data: Dict[str, Dict[str, pd.DataFrame]]) -> None:
    plt.figure(figsize=(12, 6))
    plt.style.use("default")

    colors = {
        "aks": ["#1f77b4", "#2ca02c"],
        "eks": ["#d62728", "#ff7f0e"],
        "gke": ["#9467bd", "#8c564b"],
    }

    has_data = False
    for cloud, nodes in avg_data.items():
        for i, node_label in enumerate(["node1", "node2"]):
            df = nodes.get(node_label)
            if df is None or df.empty:
                debug(f"[{cloud}] brak danych dla {node_label}")
                continue

            plt.plot(
                df.index,
                df["avg_utilisation"],
                lw=2,
                color=colors.get(cloud, ["#000", "#555"])[i % 2],
                label=f"{cloud.upper()} {node_label}",
            )
            has_data = True

    plt.axvspan(0, 10, color="lightgray", alpha=0.3, label="okres testu (10 min)")
    plt.axvline(0, color="gray", linestyle="--", lw=1)
    plt.axvline(10, color="gray", linestyle="--", lw=1)
    plt.title("Średnie zużycie CPU (stress01–03) — AKS / EKS / GKE", fontsize=13, weight="bold")
    plt.xlabel("Czas od startu testu [min]")
    plt.ylabel("Średnie zużycie CPU [%]")
    plt.grid(True, alpha=0.4)
    plt.legend(fontsize=9, loc="upper right", ncol=2)
    plt.tight_layout()

    if not has_data:
        debug("❌ Brak danych do rysowania — sprawdź ścieżki lub T₀.")
    plt.savefig(OUT_PATH, dpi=200)
    plt.close()
    debug(f"✅ Wykres zapisano: {OUT_PATH}")


def main() -> None:
    all_avg: Dict[str, Dict[str, pd.DataFrame]] = {}

    for cloud in CLOUDS:
        cloud_dir = BASE_DIR / cloud
        if not cloud_dir.exists():
            debug(f"[{cloud}] Brak katalogu {cloud_dir}")
            continue

        all_avg[cloud] = average_node_usage_for_cloud(cloud_dir)

    plot_all_clouds(all_avg)


if __name__ == "__main__":
    main()
