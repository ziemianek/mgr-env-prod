import re
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from pathlib import Path


# ===== START OF CONFIGURATION =====
K8S = "gke"  # gke / eks / aks
TEST_TYPE = "stress"  # stress / soak
# ====== END OF CONFIGURATION ======


INPUT_FILES = [
    f"./data/{K8S}/{TEST_TYPE}01/k6_results.txt",
    f"./data/{K8S}/{TEST_TYPE}02/k6_results.txt",
    f"./data/{K8S}/{TEST_TYPE}03/k6_results.txt"
]
CSV_OUTPUT = f"./data/{K8S}/{TEST_TYPE}_summary.csv"
PLOTS_OUTPUT_DIR = Path(f"data/{K8S}/{TEST_TYPE}_plots")
PLOTS_OUTPUT_DIR.mkdir(exist_ok=True)


def to_seconds(value: str) -> float:
    if not isinstance(value, str) or not value:
        return np.nan
    value = value.strip()
    if value.endswith("ms"):
        return float(value.replace("ms", "")) / 1000
    if value.endswith("m") and not value.endswith("ms"):
        return float(value.replace("m", "")) * 60
    if value.endswith("s"):
        return float(value.replace("s", ""))
    return np.nan


def to_megabytes(value: str) -> float:
    if not isinstance(value, str) or not value.strip():
        return np.nan
    value = value.replace("/s", "").strip()
    if not re.search(r"[\d\.]", value):
        return np.nan
    if "GB" in value:
        return float(re.sub(r"[^0-9.]", "", value)) * 1024
    if "MB" in value:
        return float(re.sub(r"[^0-9.]", "", value))
    if "kB" in value:
        return float(re.sub(r"[^0-9.]", "", value)) / 1024
    return float(re.sub(r"[^0-9.]", "", value))


def extract(pattern, text):
    match = re.search(pattern, text)
    return match.group(1).strip() if match else np.nan


def parse_k6_file(filepath):
    text = Path(filepath).read_text(encoding="utf-8", errors="ignore")
    data = {}

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

    return data


def summarize_cluster():
    records = []
    for f in INPUT_FILES:
        if Path(f).exists():
            records.append(parse_k6_file(f))
        else:
            print(f"⚠️ Brak pliku: {f}")

    if not records:
        raise SystemExit(f"❌ Nie znaleziono plików wynikowych dla {K8S}.")

    df = pd.DataFrame(records, index=["Test 1", "Test 2", "Test 3"])

    avg = df.mean(numeric_only=True)
    std = df.std(numeric_only=True)
    df.loc["Średnia"] = avg
    df.loc["Odchylenie std"] = std
    df = df.round(3)

    df.to_csv(CSV_OUTPUT, sep=";")
    return df


# Pomocnicza funkcja do dodawania etykiet
def add_labels(ax, bars):
    """Dodaje etykiety nad słupkami."""
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # odstęp w pionie
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

def add_point_labels(ax, x, y):
    """Dodaje etykiety dla punktów na wykresie liniowym."""
    for xi, yi in zip(x, y):
        ax.annotate(f"{yi:.2f}", (xi, yi),
                    textcoords="offset points", xytext=(0,5),
                    ha='center', fontsize=9, fontweight="bold")


if __name__ == '__main__':
    df = summarize_cluster()
    # df = df.set_index(df.columns[0])
    df_tests = df.loc[["Test 1", "Test 2", "Test 3"]]

    plt.style.use("seaborn-v0_8-colorblind")

    # =======================
    # 1️⃣ Średni czas odpowiedzi HTTP (avg, p90, p95)
    # =======================
    fig, ax = plt.subplots(figsize=(8,5))
    plt.grid(True, which="major", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    x = range(len(df_tests))
    width = 0.25

    bars1 = ax.bar([i - width for i in x], df_tests["http_req_duration_avg"], width=width, label="Średni [avg]")
    bars2 = ax.bar(x, df_tests["http_req_duration_p90"], width=width, label="p90")
    bars3 = ax.bar([i + width for i in x], df_tests["http_req_duration_p95"], width=width, label="p95")

    # Marginesy osi
    y_min, y_max = df_tests[["http_req_duration_avg", "http_req_duration_p95"]].min().min(), df_tests[["http_req_duration_avg", "http_req_duration_p95"]].max().max()
    y_range = y_max - y_min
    ax.set_ylim(y_min - 0.1*y_range, y_max + 0.15*y_range)
    ax.set_xlim(-0.5, len(df_tests.index)-0.5)

    # Oś X
    ax.set_xticks(x)
    ax.set_xticklabels(df_tests.index, fontsize=10)
    ax.set_xlabel("")
    ax.set_ylabel("Czas odpowiedzi [s]")
    ax.set_title("Średni czas odpowiedzi HTTP podczas testów stresowych GKE")

    # Etykiety z jednostkami
    for bars, unit in zip([bars1, bars2, bars3], ["s", "s", "s"]):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height:.2f} {unit}",
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha="center", va="bottom",
                        fontsize=9, fontweight="bold",
                        bbox=dict(facecolor="white", alpha=0.9, edgecolor="none"))

    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_OUTPUT_DIR / f"{K8S}_http_response_times.png", dpi=300)
    plt.close()

    # =======================
    # 2️⃣ Liczba żądań na sekundę (RPS) i współczynnik błędów
    # =======================
    fig, ax1 = plt.subplots(figsize=(8,5))
    color_rps = "tab:blue"
    color_err = "tab:red"

    # --- Siatka ---
    ax1.grid(True, which="major", linestyle="--", alpha=0.5)
    ax1.set_axisbelow(True)

    # Dane
    rps = df_tests["http_reqs_rate"]
    err = df_tests["http_req_failed_%"]

    # --- Oś lewa (RPS) ---
    ax1.set_ylabel("Żądania na sekundę [req/s]", color=color_rps)
    ax1.plot(df_tests.index, rps, marker="o", color=color_rps, linewidth=2)
    ax1.tick_params(axis="y", labelcolor=color_rps)
    ax1.set_xlabel("")
    ax1.set_xticks(range(len(df_tests.index)))
    ax1.set_xticklabels(df_tests.index, fontsize=10)

    # === Marginesy pionowe (Y) ===
    rps_min, rps_max = rps.min(), rps.max()
    rps_range = rps_max - rps_min
    ax1.set_ylim(rps_min - 0.1*rps_range, rps_max + 0.15*rps_range)

    # === Marginesy poziome (X) ===
    ax1.set_xlim(-0.3, len(df_tests.index) - 0.7)  # dodaje odstęp z lewej i prawej

    # --- Etykiety RPS ---
    for i, (x, y) in enumerate(zip(range(len(rps)), rps)):
        ax1.annotate(f"{y:.2f} req/s",
                    xy=(x, y),
                    xytext=(0, 8),
                    textcoords="offset points",
                    ha="center", va="bottom",
                    fontsize=9, fontweight="bold", color=color_rps,
                    bbox=dict(facecolor="white", alpha=0.9, edgecolor="none"))

    # --- Druga oś: błędy HTTP ---
    ax2 = ax1.twinx()
    ax2.set_ylabel("Błędy HTTP [%]", color=color_err)
    ax2.plot(df_tests.index, err, marker="s", linestyle="--", color=color_err, linewidth=2)
    ax2.tick_params(axis="y", labelcolor=color_err)

    # Marginesy dla błędów
    err_min, err_max = err.min(), err.max()
    err_range = err_max - err_min if err_max != err_min else err_max * 0.1
    ax2.set_ylim(err_min - 0.15*err_range, err_max + 0.20*err_range)

    # --- Etykiety błędów HTTP ---
    for i, (x, y) in enumerate(zip(range(len(err)), err)):
        ax2.annotate(f"{y:.2f} %",
                    xy=(x, y),
                    xytext=(0, 8),
                    textcoords="offset points",
                    ha="center", va="bottom",
                    fontsize=9, fontweight="bold", color=color_err,
                    bbox=dict(facecolor="white", alpha=0.9, edgecolor="none"))

    # --- Tytuł i zapis ---
    plt.title("Liczba żądań i błędów HTTP podczas testów stresowych GKE")
    fig.tight_layout()
    fig.savefig(PLOTS_OUTPUT_DIR / f"{K8S}_rps_vs_errors.png", dpi=300)
    plt.close()

    # =======================
    # 3️⃣ Transfer danych sieciowych (MB/s)
    # =======================
    fig, ax = plt.subplots(figsize=(8,5))
    plt.grid(True, which="major", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    width = 0.35
    x = range(len(df_tests))

    bars_rx = ax.bar([i - width/2 for i in x], df_tests["data_received_rate_MBps"], width=width, label="Odebrane [MB/s]")
    bars_tx = ax.bar([i + width/2 for i in x], df_tests["data_sent_rate_MBps"], width=width, label="Wysłane [MB/s]")

    # --- Marginesy minimalne (bez odstępu po bokach) ---
    y_min, y_max = df_tests[["data_received_rate_MBps", "data_sent_rate_MBps"]].min().min(), df_tests[["data_received_rate_MBps", "data_sent_rate_MBps"]].max().max()
    y_range = y_max - y_min
    ax.set_ylim(0, y_max + 0.25*y_range)  # zaczyna się od 0, tylko górny margines

    # Oś X
    ax.set_xticks(x)
    ax.set_xticklabels(df_tests.index, fontsize=10)
    ax.set_xlabel("")
    ax.set_ylabel("Przepływ danych [MB/s]")
    ax.set_title("Transfer danych podczas testów stresowych GKE")

    # Etykiety z jednostkami
    for bars, unit in zip([bars_rx, bars_tx], ["MB/s", "MB/s"]):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height:.2f} {unit}",
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha="center", va="bottom",
                        fontsize=9, fontweight="bold",
                        bbox=dict(facecolor="white", alpha=0.9, edgecolor="none"))

    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_OUTPUT_DIR / f"{K8S}_network_transfer.png", dpi=300)
    plt.close()

    # =======================
    # 4️⃣ Iteration Duration (średni i p95)
    # =======================
    fig, ax = plt.subplots(figsize=(8,5))
    plt.grid(True, which="major", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    width = 0.35
    x = range(len(df_tests))
    bars_avg = ax.bar([i - width/2 for i in x], df_tests["iteration_duration_avg"], width=width, label="Średni czas iteracji")
    bars_p95 = ax.bar([i + width/2 for i in x], df_tests["iteration_duration_p95"], width=width, label="p95")

    # Marginesy
    y_min, y_max = df_tests[["iteration_duration_avg", "iteration_duration_p95"]].min().min(), df_tests[["iteration_duration_avg", "iteration_duration_p95"]].max().max()
    y_range = y_max - y_min
    ax.set_ylim(y_min - 0.1*y_range, y_max + 0.15*y_range)
    ax.set_xlim(-0.5, len(df_tests.index)-0.5)

    # Oś X
    ax.set_xticks(x)
    ax.set_xticklabels(df_tests.index, fontsize=10)
    ax.set_xlabel("")
    ax.set_ylabel("Czas iteracji [s]")
    ax.set_title("Czas wykonania iteracji testowych (iteration duration) w GKE")

    # Etykiety z jednostkami
    for bars, unit in zip([bars_avg, bars_p95], ["s", "s"]):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height:.2f} {unit}",
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha="center", va="bottom",
                        fontsize=9, fontweight="bold",
                        bbox=dict(facecolor="white", alpha=0.9, edgecolor="none"))

    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_OUTPUT_DIR / f"{K8S}_iteration_duration.png", dpi=300)
    plt.close()

    # =======================
    # Podsumowanie
    # =======================
    print("✅ Wygenerowano wykresy z etykietami (zaokrąglone do 2 miejsc):")
    for f in PLOTS_OUTPUT_DIR.glob("*.png"):
        print(" -", f)
