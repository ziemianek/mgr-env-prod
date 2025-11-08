import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from pathlib import Path

# =================== KONFIG ===================
BASE_DIR = Path("data/gke")
OUT_DIR = Path("results/gke_rps_errors_rate")
OUT_DIR.mkdir(parents=True, exist_ok=True)

T0_MAP = {
    "stress01": pd.Timestamp("2025-10-17 20:09:30"),
    "stress02": pd.Timestamp("2025-10-18 07:36:00"),
    "stress03": pd.Timestamp("2025-10-18 08:51:30"),
}

FILES = {
    "requests": "Total Requests (increase over 1m).csv",
    "errors": "Error Rate (4xx + 5xx).csv",
}

X_MIN, X_MAX = -2, 12
TEST_START, TEST_END = 0, 10


# =================== FUNKCJE ===================
def load_series(path):
    df = pd.read_csv(path)
    if df["Time"].astype(str).str.isnumeric().all():
        df["Time"] = pd.to_datetime(df["Time"], unit="ms", errors="coerce")
    else:
        df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    df = df.dropna(subset=["Time"]).set_index("Time").sort_index()
    col = df.columns[-1]
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df[[col]]


def align_to_t0(df, t0, step=0.5):
    df = df.copy()
    df.index = (df.index - t0).total_seconds() / 60.0
    df = df[df.index >= 0]
    if df.empty:
        return df
    new_index = np.arange(df.index.min(), df.index.max(), step)
    df = df.reindex(df.index.union(new_index)).interpolate().reindex(new_index)
    df.index.name = "minutes_from_t0"
    df = df.fillna(0)
    return df


def aggregate_tests(metric):
    dfs = []
    for test, t0 in T0_MAP.items():
        path = BASE_DIR / test / FILES[metric]
        if not path.exists():
            print(f"⚠️ Brak pliku: {path}")
            continue
        df = align_to_t0(load_series(path), t0)
        dfs.append(df)
    if not dfs:
        raise SystemExit(f"Brak danych dla {metric}")
    return pd.concat(dfs).groupby(level=0).mean().sort_index()


# =================== GŁÓWNY BLOK ===================
print("📈 Przetwarzanie danych HTTP (requests/errors/rate) dla GKE...")
requests = aggregate_tests("requests")
errors = aggregate_tests("errors")

combined = requests.join(errors, how="inner")
combined.columns = ["requests", "errors"]
combined["error_rate"] = np.where(combined["requests"] > 0,
                                  100 * combined["errors"] / combined["requests"], 0)

combined = combined[(combined.index >= X_MIN) & (combined.index <= X_MAX)]

# =================== WYKRES ===================
fig, ax1 = plt.subplots(figsize=(11, 6))
ax2 = ax1.twinx()

# ⬇️ 1) RYSOWANIE – przenieś error_rate na LEWĄ oś,
# a requests/errors na PRAWĄ oś
ax1.plot(combined.index, combined["error_rate"], color="#ff7f0e", lw=2, linestyle="--",
         label="Wskaźnik błędów [%]")

ax2.plot(combined.index, combined["requests"], color="#1f77b4", lw=2,
         label="Liczba żądań [req/min]")
ax2.plot(combined.index, combined["errors"], color="#d62728", lw=2,
         label="Błędy HTTP 4xx+5xx [req/min]")

# tło i linie pozostają na ax1 (bez zmian)
ax1.axvspan(TEST_START, TEST_END, color="lightgray", alpha=0.3, label="Czas trwania testu")
ax1.axvline(TEST_START, color="#2b8cbe", linestyle="--", lw=1.2)
ax1.axvline(TEST_END, color="#2b8cbe", linestyle="--", lw=1.2)

# ⬇️ 2) OPISY OSI – zamień podpisy
ax1.set_xlim(X_MIN, X_MAX)
ax1.xaxis.set_major_locator(MultipleLocator(1))
ax1.set_xlabel("Czas od rozpoczęcia testu [min]")
ax1.set_ylabel("Wskaźnik błędów [%]")                 # <-- teraz po lewej
ax2.set_ylabel("Liczba żądań / Błędy [req/min]")      # <-- teraz po prawej

# (opcjonalnie) dopasuj kolory etykiet osi
# ax1.tick_params(axis="y", labelcolor="#ff7f0e")
# ax2.tick_params(axis="y", labelcolor="#1f77b4")

ax1.grid(True, alpha=0.25)
fig.suptitle("Liczba żądań, błędów i wskaźnik błędów HTTP podczas testów stresowych GKE")

# ⬇️ 3) LEGENDA – zbierz oba zbiory linii (bez zmian)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
fig.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(0.1, 0.93), fontsize=9)

fig.tight_layout()
out_path = OUT_DIR / "gke_rps_errors_rate_stress.png"
plt.savefig(out_path, dpi=200)
plt.close()

combined.to_csv(OUT_DIR / "gke_rps_errors_rate_series.csv")
print(f"✅ Wykres zapisano w {out_path}")
