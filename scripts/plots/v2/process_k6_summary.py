import matplotlib.pyplot as plt
import pandas as pd

from pathlib import Path


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Plik nie istnieje: {path}")
    return pd.read_csv(path, sep=';', encoding='utf-8', engine='python')


def extract_avg_http_metrics(df: pd.DataFrame) -> pd.Series:
    selected_columns: list[str] = [
        "http_req_duration_avg",
        "http_req_duration_p90",
        "http_req_duration_p95",
        "http_req_failed_%",
    ]

    missing = [col for col in selected_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Brakujące kolumny w DataFrame: {missing}")

    mask = df.iloc[:, 0].astype(str).str.strip().str.lower() == "średnia"
    avg_row = df.loc[mask]
    
    if avg_row.empty:
        raise ValueError("Brak wiersza 'Średnia' w podanym DataFrame.")

    return avg_row[selected_columns].squeeze()


def compare_avg_http_metrics(dataframes: list[pd.DataFrame]) -> pd.DataFrame:
    results = {}

    for k8s, df in dataframes.items():
        avg_metrics = extract_avg_http_metrics(df)
        results[k8s] = avg_metrics

    # Złożenie wszystkiego w jeden DataFrame
    comparison_df = pd.DataFrame(results).T  # transpozycja: testy jako wiersze
    return comparison_df


def plot_metrics(df: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.style.use("seaborn-v0_8-muted")  # elegancki, stonowany styl

    for column in df.columns:
        plt.figure(figsize=(8, 5))
        df[column].plot(kind="bar", color="steelblue", edgecolor="black")

        plt.title(f"Porównanie {column}", fontsize=14, weight="bold")
        plt.ylabel(column, fontsize=12)
        plt.xlabel("Środowisko", fontsize=12)
        plt.xticks(rotation=0)
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        # Dodanie etykiet wartości nad słupkami
        for idx, value in enumerate(df[column]):
            plt.text(idx, value, f"{value:.2f}", ha="center", va="bottom", fontsize=10)

        plt.tight_layout()
        output_path = output_dir / f"{column}.png"
        plt.savefig(output_path, dpi=150)
        plt.close()

        print(f"✅ Zapisano wykres: {output_path}")

def plot_combined_duration_chart(df: pd.DataFrame, output_path: Path) -> None:
    selected_columns = [
        "http_req_duration_avg",
        "http_req_duration_p90",
        "http_req_duration_p95",
        "http_req_failed_%",
    ]

    # Sprawdzenie kolumn
    missing = [col for col in selected_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Brakujące kolumny w DataFrame: {missing}")

    # Wybór danych i zmiana nazw kolumn dla czytelności na wykresie
    data = df[selected_columns].rename(
        columns={
            "http_req_duration_avg": "Średnia",
            "http_req_duration_p90": "p90",
            "http_req_duration_p95": "p95",
            # "http_req_failed_%": "Błędy [%]",
        }
    )

    plt.style.use("seaborn-v0_8-muted")
    ax = data[["Średnia", "p90", "p95"]].plot(
        kind="bar",
        figsize=(10, 6),
        width=0.75,
        edgecolor="black",
    )

    # Oś i tytuł
    ax.set_title("Porownanie czasu odpowiedzi HTTP w testach stresu", fontsize=14, weight="bold")
    ax.set_ylabel("Czas odpowiedzi [s]", fontsize=12)
    ax.set_xlabel("Środowisko", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    ax.legend(title="Metryka", loc="upper left")

    # Dodanie wartości nad słupkami
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f s", label_type="edge", fontsize=10, padding=2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"✅ Wykres zapisano do: {output_path}")


def main() -> None:
    k6_gke_path = Path("./data/gke/soak_summary.csv")
    k6_aks_path = Path("./data/aks/soak_summary.csv")
    # k6_eks_path = Path("./data/eks/stress_summary.csv")

    dataframes = {
        "gke": load_csv(k6_gke_path),
        "aks": load_csv(k6_aks_path)
    }

    comparison_df = compare_avg_http_metrics(dataframes)
    print(comparison_df.head())

    # plot_metrics(comparison_df, Path("./results"))
    plot_combined_duration_chart(comparison_df, Path("./results/http_latency_combined.png"))


if __name__ == "__main__":
    main()
