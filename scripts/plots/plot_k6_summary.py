import matplotlib.pyplot as plt
import pandas as pd
import sys

from scripts.utils.logger import *


# === CONFIG ===
# TEST_TYPE = "stress"
TEST_TYPE = "soak"
PATH = f"./data/k6_{TEST_TYPE.lower()}_results_summary.csv"
REQ_DURATION_PLOT_OUTPUT_PATH = f"./results/mean_http_req_duration_{TEST_TYPE.lower()}_plot.png"
ERRORS_PLOT_OUTPUT_PATH = f"./results/mean_http_req_error_rate_{TEST_TYPE.lower()}_plot.png"
# === END OF CONFIG ===


def mean_k6_stats(df: pd.DataFrame) -> pd.DataFrame:
    df["cluster"] = df["Unnamed: 0"].str.split("-").str[0]
    metrics = [
        "http_req_duration_avg",
        "http_req_duration_p90",
        "http_req_duration_p95",
        "http_req_failed_%"
    ]
    cluster_means = df.groupby("cluster")[metrics].mean()
    print_debug("Calculated mean stats")
    return cluster_means


def dry_run() -> bool:
    if len(sys.argv) == 1:
        return False
    return sys.argv[1] == "--dry-run"


def plot_response_time(df: pd.DataFrame) -> None:
    ax = df[[
        "http_req_duration_avg",
        "http_req_duration_p90",
        "http_req_duration_p95"
    ]].plot(kind="bar")
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(
            f"{height:.2f}",
            (p.get_x() + p.get_width() / 2, height),
            ha="center", va="bottom", fontsize=8, rotation=0
        )
    plt.xlabel("Cluster")
    plt.ylabel("Duration (s)")
    plt.title("Average, P90, P95 HTTP Request Duration per Cluster")
    plt.tight_layout()
    if not dry_run():
        plt.savefig(REQ_DURATION_PLOT_OUTPUT_PATH, dpi=200)
        print_debug(f"Saved Req Duration Plot to {REQ_DURATION_PLOT_OUTPUT_PATH}")
    else:
        plt.show()


def plot_error_rates(df: pd.DataFrame) -> None:
    df["cluster"] = df.index
    cluster_colors = {
        "aks": "blue",
        "gke": "green",
        "eks": "orange"
    }
    colors = [cluster_colors.get(c, "gray") for c in df["cluster"]]
    plt.figure(figsize=(12, 6))
    ax = plt.bar(
        x=df["cluster"].str.upper(),
        height=df["http_req_failed_%"],
        color=colors,
        zorder=3
    )
    for p in ax:
        height = p.get_height()
        plt.text(
            p.get_x() + p.get_width() / 2,
            height,
            f"{height:.2f} %",
            ha="center",
            va="bottom",
            fontsize=12,
            zorder=4
        )
    plt.xlabel("Klaster")
    plt.ylabel("Współczynnik błędów (%)")
    plt.title("Współczynnik błędów HTTP dla klastrów")
    legend_handles = [
        plt.Line2D([0], [0], marker="s", color=color, lw=0, markersize=10, label=cluster.upper())
        for cluster, color in cluster_colors.items()
        if cluster in df["cluster"].unique()
    ]
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(handles=legend_handles, loc="upper right")
    plt.tight_layout()
    if not dry_run():
        plt.savefig(ERRORS_PLOT_OUTPUT_PATH, dpi=200)
        print_debug(f"Saved Error Plot to {ERRORS_PLOT_OUTPUT_PATH}")
    else:
        plt.show()


def main():
    df = pd.read_csv(PATH)
    print_debug(f"Loaded data from {PATH}")
    res = mean_k6_stats(df)
    print_debug(f"Result DataFrame head:\n{res.head()}")
    plot_response_time(res)
    plot_error_rates(res)


if __name__ == "__main__":
    main()