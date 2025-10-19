import pandas as pd
from pathlib import Path

# === KONFIG ===
BASE_DIR = Path("data/gke")
OUT_DIR = Path("results/gke_latency_stats")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TESTS = ["stress01", "stress02", "stress03"]

FILES = {
    "avg": "Average Request Duration (ms).csv",
    "p95": "95th Percentile Latency (ms).csv",
}


def load_series(path):
    """Wczytuje CSV z kolumną Time i jedną kolumną metryki."""
    df = pd.read_csv(path)
    # konwersja czasu
    if df["Time"].astype(str).str.isnumeric().all():
        df["Time"] = pd.to_datetime(df["Time"], unit="ms", errors="coerce")
    else:
        df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    df = df.dropna(subset=["Time"]).set_index("Time")

    # konwersja do float
    value_col = df.columns[0]
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    return df.dropna()


def compute_latency_stats(test_name):
    """Zwraca statystyki (średnia, min, max, p95) dla danego testu."""
    test_dir = BASE_DIR / test_name
    results = {}

    for metric, filename in FILES.items():
        path = test_dir / filename
        if not path.exists():
            print(f"⚠️ Brak pliku: {path}")
            continue

        df = load_series(path)
        col = df.columns[0]

        results[f"{metric}_mean"] = df[col].mean()
        results[f"{metric}_median"] = df[col].median()
        results[f"{metric}_min"] = df[col].min()
        results[f"{metric}_max"] = df[col].max()

    return results


def main():
    summary = []

    for test in TESTS:
        print(f"📊 Przetwarzanie {test} ...")
        stats = compute_latency_stats(test)
        summary.append({"test": test, **stats})

    df_summary = pd.DataFrame(summary)
    df_summary.to_csv(OUT_DIR / "gke_latency_summary.csv", index=False)

    print("\n=== Średnie czasy odpowiedzi (Grafana) ===")
    print(df_summary[["test", "avg_mean", "p95_mean"]].round(2))
    print("\n✅ Wyniki zapisano do:", OUT_DIR / "gke_latency_summary.csv")


if __name__ == "__main__":
    main()
