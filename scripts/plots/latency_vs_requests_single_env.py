import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from pathlib import Path

# ====================== KONFIG ======================
BASE_DIR = Path("data/gke")
OUT_DIR  = Path("results/gke_latency_rps")
OUT_DIR.mkdir(parents=True, exist_ok=True)


T0_MAP = {
    "stress01": pd.Timestamp("2025-10-17 20:09:30"),
    "stress02": pd.Timestamp("2025-10-18 07:36:00"),
    "stress03": pd.Timestamp("2025-10-18 08:51:30"),
}

LAT_AVG_FILE = "Average Request Duration (ms).csv"
LAT_P95_FILE = "95th Percentile Latency (ms).csv"
REQ_FILE     = "Total Requests (increase over 1m).csv"

X_MIN, X_MAX = -2, 12
TEST_START, TEST_END = 0, 10


# ====================== FUNKCJE ======================
def load_series(path: Path) -> pd.DataFrame:
    """Wczytaj CSV (Time,<value>) i zwróć DataFrame z datetime indexem."""
    if not path.exists():
        raise FileNotFoundError(f"Brak pliku: {path}")
    df = pd.read_csv(path)
    if pd.api.types.is_numeric_dtype(df["Time"]) or df["Time"].astype(str).str.isnumeric().all():
        df["Time"] = pd.to_datetime(df["Time"], unit="ms", errors="coerce")
    else:
        df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    df = df.dropna(subset=["Time"]).set_index("Time").sort_index()
    col = df.columns[0]
    df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna()


def align_cut_interpolate(df: pd.DataFrame, t0: pd.Timestamp, step_min: float = 0.5) -> pd.DataFrame:
    """Wyrównaj do t0 (minuty), utnij <0, zinterpoluj do stałego kroku, zamień NaN na 0."""
    out = df.copy()
    out.index = (out.index - t0).total_seconds() / 60.0
    out = out[out.index >= 0]  # usuń baseline
    if out.empty:
        return out
    out = out.sort_index()
    new_idx = np.arange(out.index.min(), out.index.max() + 1e-9, step_min)
    out = out.reindex(out.index.union(new_idx)).interpolate().reindex(new_idx)
    out.index.name = "min_from_t0"
    # ⚙️ zamień NaN na 0
    out = out.fillna(0)
    return out


def prepare_one_test(test_name: str, t0: pd.Timestamp) -> pd.DataFrame:
    """Zbuduj wspólny DF [latency_avg, latency_p95, requests] dla pojedynczego testu."""
    base = BASE_DIR / test_name
    lat_avg = align_cut_interpolate(load_series(base / LAT_AVG_FILE), t0)
    lat_p95 = align_cut_interpolate(load_series(base / LAT_P95_FILE), t0)
    reqs    = align_cut_interpolate(load_series(base / REQ_FILE), t0)

    lat_avg.columns = ["latency_avg"]
    lat_p95.columns = ["latency_p95"]
    reqs.columns    = ["requests"]

    df = lat_avg.join(lat_p95, how="inner").join(reqs, how="inner")
    # ✂️ przytnij oś X do 12 minut
    df = df[(df.index >= X_MIN) & (df.index <= X_MAX)]
    return df.fillna(0)


# ====================== GŁÓWNY PRZEBIEG ======================
per_test = []
for test, t0 in T0_MAP.items():
    try:
        df = prepare_one_test(test, t0)
        if df.empty:
            print(f"⚠️ Pusty wynik po t₀ dla {test}")
            continue
        per_test.append(df)
        print(f"✅ {test}: zakres względem t₀ -> {df.index.min():.2f} do {df.index.max():.2f} min")
    except Exception as e:
        print(f"⚠️ Błąd w {test}: {e}")

if not per_test:
    raise SystemExit("Brak danych do narysowania.")

combined = pd.concat(per_test).groupby(level=0).mean().sort_index()

# ====================== WYKRES ======================
fig, ax1 = plt.subplots(figsize=(11, 6))
ax2 = ax1.twinx()

# Linie główne
ax1.plot(combined.index, combined["latency_avg"], color="#1f77b4", lw=2.2, label="Czas odpowiedzi [ms]")
ax1.plot(combined.index, combined["latency_p95"], color="#ff7f0e", lw=2.2, label="Czas odpowiedzi (95. percentyl) [ms]")
ax2.plot(combined.index, combined["requests"],     color="#2ca02c", lw=2.0, alpha=0.75, label="Liczba żądań [req/min]")

# tło testu
ax1.axvspan(TEST_START, TEST_END, color="lightgray", alpha=0.3, label="Czas trwania testu")
ax1.axvline(TEST_START, color="#2b8cbe", linestyle="--", lw=1.2)
ax1.axvline(TEST_END,   color="#2b8cbe", linestyle="--", lw=1.2)

# osie i styl
ax1.set_xlim(X_MIN, X_MAX)
ax1.xaxis.set_major_locator(MultipleLocator(1))
ax1.set_xlabel("Czas od rozpoczęcia testu [min]")
ax1.set_ylabel("Czas odpowiedzi [ms]")
ax2.set_ylabel("Liczba żądań [req/min]")
ax1.grid(True, alpha=0.35)

fig.suptitle("Zależność między liczbą żądań a czasami odpowiedzi (stress testy, znormalizowane do t₀)")

# legenda
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
fig.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(0.1, 0.93), fontsize=9)

fig.tight_layout()
out_path = OUT_DIR / "latency_vs_requests.png"
plt.savefig(out_path, dpi=200)
plt.close()

combined.to_csv(OUT_DIR / "latency_vs_requests_series.csv")
print(f"✅ Zapisano wykres: {out_path}")
