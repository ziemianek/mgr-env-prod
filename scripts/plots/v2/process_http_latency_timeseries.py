# #!/usr/bin/env python3
# """
# Moduł do łączenia metryk wydajności w czasie (requests, p95 latency, avg latency).
# Autor: Michał Ziemianek
# """

# from pathlib import Path
# import pandas as pd
# import matplotlib.pyplot as plt


# def load_time_series_data(
#     requests_path: Path,
#     p95_latency_path: Path,
#     avg_latency_path: Path,
# ) -> pd.DataFrame:
#     """
#     Wczytuje dane z trzech plików CSV i łączy je w jeden DataFrame na podstawie kolumny 'Time'.

#     Każdy plik ma tę samą liczbę wierszy i kolumnę 'Time'.

#     :param requests_path: Ścieżka do pliku z liczbą zapytań w czasie
#     :param p95_latency_path: Ścieżka do pliku z 95. percentylem opóźnień (ms)
#     :param avg_latency_path: Ścieżka do pliku ze średnim opóźnieniem (ms)
#     :return: DataFrame z kolumnami ['Time', 'requests', 'p95_latency_ms', 'avg_duration_ms']
#     """
#     # Wczytanie plików
#     df_requests = pd.read_csv(requests_path)
#     df_p95 = pd.read_csv(p95_latency_path)
#     df_avg = pd.read_csv(avg_latency_path)

#     # Walidacja długości
#     if not (len(df_requests) == len(df_p95) == len(df_avg)):
#         raise ValueError("Pliki muszą mieć taką samą liczbę wierszy!")

#     # Normalizacja nazw kolumn
#     df_requests.columns = ["Time", "requests"]
#     df_p95.columns = ["Time", "p95_latency_ms"]
#     df_avg.columns = ["Time", "avg_duration_ms"]

#     # Konwersja Time na datetime (jeśli to timestamp w milisekundach)
#     df_requests["Time"] = pd.to_datetime(df_requests["Time"], unit="ms")
#     df_p95["Time"] = pd.to_datetime(df_p95["Time"], unit="ms")
#     df_avg["Time"] = pd.to_datetime(df_avg["Time"], unit="ms")

#     # Łączenie po kolumnie 'Time'
#     merged = (
#         df_requests
#         .merge(df_p95, on="Time", how="left")
#         .merge(df_avg, on="Time", how="left")
#         .sort_values("Time")
#         .reset_index(drop=True)
#     )

#     return merged

# def plot_latency_over_time(df: pd.DataFrame, output_path: Path = Path("latency_over_time.png")) -> None:
#     """
#     Tworzy wykres pokazujący, jak zmieniały się opóźnienia (avg i p95) oraz liczba zapytań w czasie.
#     Oś X: czas
#     Lewa oś Y: opóźnienie [ms]
#     Prawa oś Y: liczba zapytań

#     :param df: DataFrame z kolumnami ['Time', 'requests', 'p95_latency_ms', 'avg_duration_ms']
#     :param output_path: Ścieżka, do której zapisany zostanie wykres PNG
#     """
#     required_cols = {"Time", "requests", "p95_latency_ms", "avg_duration_ms"}
#     if not required_cols.issubset(df.columns):
#         raise ValueError(f"DataFrame musi zawierać kolumny: {required_cols}")

#     # Konwersja Time do datetime (jeśli jeszcze nie jest)
#     if not pd.api.types.is_datetime64_any_dtype(df["Time"]):
#         df["Time"] = pd.to_datetime(df["Time"], unit="ms", errors="ignore")

#     plt.style.use("seaborn-v0_8-muted")
#     fig, ax1 = plt.subplots(figsize=(11, 6))

#     # Lewa oś — opóźnienia
#     ax1.plot(
#         df["Time"],
#         df["avg_duration_ms"],
#         label="Średnie opóźnienie [ms]",
#         color="tab:blue",
#         linewidth=2,
#         marker="o",
#     )
#     ax1.plot(
#         df["Time"],
#         df["p95_latency_ms"],
#         label="95. percentyl opóźnień [ms]",
#         color="tab:orange",
#         linewidth=2,
#         marker="s",
#     )
#     ax1.set_xlabel("Czas", fontsize=12)
#     ax1.set_ylabel("Opóźnienie [ms]", fontsize=12, color="tab:blue")
#     ax1.tick_params(axis="y", labelcolor="tab:blue")
#     ax1.grid(True, linestyle="--", alpha=0.6)

#     # Prawa oś — liczba zapytań
#     ax2 = ax1.twinx()
#     ax2.plot(
#         df["Time"],
#         df["requests"],
#         label="Liczba zapytań",
#         color="tab:green",
#         linewidth=2,
#         linestyle="--",
#         alpha=0.8,
#     )
#     ax2.set_ylabel("Liczba zapytań", fontsize=12, color="tab:green")
#     ax2.tick_params(axis="y", labelcolor="tab:green")

#     # Tytuł i legenda
#     fig.suptitle("Zmiana opóźnień i liczby zapytań w czasie", fontsize=14, weight="bold")

#     # Zbiorcza legenda
#     lines, labels = ax1.get_legend_handles_labels()
#     lines2, labels2 = ax2.get_legend_handles_labels()
#     ax1.legend(lines + lines2, labels + labels2, loc="upper left")

#     plt.tight_layout()
#     plt.savefig(output_path, dpi=150)
#     plt.close()
#     print(f"✅ Wykres zapisano do: {output_path}")


# def main() -> None:
#     """Przykładowe użycie funkcji."""

#     requests_path = Path("data/aks/stress03/Total Requests (increase over 1m).csv")
#     p95_latency_path = Path("data/aks/stress03/95th Percentile Latency (ms).csv")
#     avg_latency_path = Path("data/aks/stress03/Average Request Duration (ms).csv")

#     df = load_time_series_data(requests_path, p95_latency_path, avg_latency_path)
#     print("\n✅ Połączone dane:")
#     print(df[20:40])

#     plot_latency_over_time(df, Path(f"stress03-latencyovertime.png"))


# if __name__ == "__main__":
#     main()








# from pathlib import Path
# import pandas as pd
# from typing import List
# from matplotlib import pyplot as plt


# def load_time_series_data(requests_path: Path, p95_latency_path: Path, avg_latency_path: Path) -> pd.DataFrame:
#     df_requests = pd.read_csv(requests_path)
#     df_p95 = pd.read_csv(p95_latency_path)
#     df_avg = pd.read_csv(avg_latency_path)

#     df_requests.columns = ["Time", "requests"]
#     df_p95.columns = ["Time", "p95_latency_ms"]
#     df_avg.columns = ["Time", "avg_duration_ms"]

#     df_requests["Time"] = pd.to_datetime(df_requests["Time"], unit="ms", errors="ignore")
#     df_p95["Time"] = pd.to_datetime(df_p95["Time"], unit="ms", errors="ignore")
#     df_avg["Time"] = pd.to_datetime(df_avg["Time"], unit="ms", errors="ignore")

#     merged = (
#         df_requests.merge(df_p95, on="Time", how="outer")
#         .merge(df_avg, on="Time", how="outer")
#         .sort_values("Time")
#         .reset_index(drop=True)
#     )

#     return merged


# def resample_and_interpolate(df: pd.DataFrame, freq: str = "30S") -> pd.DataFrame:
#     """Resampluje dane do wspólnego interwału czasowego i interpoluje NaN."""
#     df = df.set_index("Time").resample(freq).mean().interpolate(method="linear").reset_index()
#     return df


# def average_iterations(dfs: List[pd.DataFrame], freq: str = "30S") -> pd.DataFrame:
#     """Uśrednia dane z wielu iteracji po czasie."""
#     dfs_resampled = [resample_and_interpolate(df, freq) for df in dfs]

#     # połączenie na wspólnym Time
#     merged = dfs_resampled[0][["Time"]].copy()
#     for col in ["requests", "p95_latency_ms", "avg_duration_ms"]:
#         merged[col] = sum(df[col] for df in dfs_resampled) / len(dfs_resampled)
#     return merged


# def plot_latency_over_time(df: pd.DataFrame, output_path: Path = Path("latency_avg_over_time.png")) -> None:
#     plt.style.use("seaborn-v0_8-muted")
#     fig, ax1 = plt.subplots(figsize=(11, 6))

#     ax1.plot(df["Time"], df["avg_duration_ms"], label="Średnie opóźnienie [ms]", color="tab:blue", marker="o")
#     ax1.plot(df["Time"], df["p95_latency_ms"], label="95. percentyl opóźnień [ms]", color="tab:orange", marker="s")
#     ax1.set_xlabel("Czas")
#     ax1.set_ylabel("Opóźnienie [ms]", color="tab:blue")
#     ax1.tick_params(axis="y", labelcolor="tab:blue")
#     ax1.grid(True, linestyle="--", alpha=0.6)

#     ax2 = ax1.twinx()
#     ax2.plot(df["Time"], df["requests"], label="Liczba zapytań", color="tab:green", linestyle="--", alpha=0.8)
#     ax2.set_ylabel("Liczba zapytań", color="tab:green")
#     ax2.tick_params(axis="y", labelcolor="tab:green")

#     lines, labels = ax1.get_legend_handles_labels()
#     lines2, labels2 = ax2.get_legend_handles_labels()
#     ax1.legend(lines + lines2, labels + labels2, loc="upper left")

#     plt.title("Średnie opóźnienie i liczba zapytań w czasie (uśrednione 3 iteracje)", fontsize=13, weight="bold")
#     plt.tight_layout()
#     plt.savefig(output_path, dpi=150)
#     plt.close()
#     print(f"✅ Wykres zapisano do: {output_path}")


# def main() -> None:
#     """Ładuje trzy iteracje testów i generuje uśredniony wykres."""
#     base = Path("data/aks")

#     iterations = ["stress01", "stress02", "stress03"]
#     dfs = []

#     for it in iterations:
#         df = load_time_series_data(
#             base / it / "Total Requests (increase over 1m).csv",
#             base / it / "95th Percentile Latency (ms).csv",
#             base / it / "Average Request Duration (ms).csv",
#         )
#         dfs.append(df)

#     df_avg = average_iterations(dfs, freq="30S")
#     print("\n✅ Uśrednione dane:")
#     print(df_avg.head())

#     plot_latency_over_time(df_avg)


# if __name__ == "__main__":
#     main()






from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from typing import List


def load_time_series_data(requests_path: Path, p95_latency_path: Path, avg_latency_path: Path) -> pd.DataFrame:
    """Ładuje i scala dane z 3 metryk dla jednej iteracji testu."""
    df_requests = pd.read_csv(requests_path)
    df_p95 = pd.read_csv(p95_latency_path)
    df_avg = pd.read_csv(avg_latency_path)

    df_requests.columns = ["Time", "requests"]
    df_p95.columns = ["Time", "p95_latency_ms"]
    df_avg.columns = ["Time", "avg_duration_ms"]

    df_requests["Time"] = pd.to_datetime(df_requests["Time"], unit="ms", errors="ignore")
    df_p95["Time"] = pd.to_datetime(df_p95["Time"], unit="ms", errors="ignore")
    df_avg["Time"] = pd.to_datetime(df_avg["Time"], unit="ms", errors="ignore")

    merged = (
        df_requests.merge(df_p95, on="Time", how="outer")
        .merge(df_avg, on="Time", how="outer")
        .sort_values("Time")
        .reset_index(drop=True)
    )
    return merged


def resample_and_interpolate(df: pd.DataFrame, freq: str = "30S") -> pd.DataFrame:
    """Resampluje dane do wspólnego interwału czasowego i interpoluje brakujące wartości."""
    df = df.set_index("Time").resample(freq).mean().interpolate(method="linear").reset_index()
    return df


def average_iterations(dfs: List[pd.DataFrame], freq: str = "30S") -> pd.DataFrame:
    """Uśrednia dane i wylicza odchylenie standardowe z wielu iteracji testów."""
    dfs_resampled = [resample_and_interpolate(df, freq) for df in dfs]

    # Wyrównanie czasów względem pierwszego zestawu
    common_time = dfs_resampled[0]["Time"]
    merged = pd.DataFrame({"Time": common_time})

    # oblicz średnie i std dla każdej kolumny
    for col in ["requests", "p95_latency_ms", "avg_duration_ms"]:
        values = pd.concat([df[col] for df in dfs_resampled], axis=1)
        merged[f"{col}_mean"] = values.mean(axis=1)
        merged[f"{col}_std"] = values.std(axis=1)

    return merged


def plot_latency_over_time(df: pd.DataFrame, output_path: Path = Path("latency_avg_with_std.png")) -> None:
    """Rysuje wykres uśrednionych metryk z pasmem odchylenia standardowego."""
    plt.style.use("seaborn-v0_8-muted")
    fig, ax1 = plt.subplots(figsize=(11, 6))

    # Średnie linie
    ax1.plot(df["Time"], df["avg_duration_ms_mean"], label="Średnie opóźnienie [ms]", color="tab:blue", linewidth=2)
    ax1.fill_between(
        df["Time"],
        df["avg_duration_ms_mean"] - df["avg_duration_ms_std"],
        df["avg_duration_ms_mean"] + df["avg_duration_ms_std"],
        color="tab:blue",
        alpha=0.2,
        label="±1σ (avg)"
    )

    ax1.plot(df["Time"], df["p95_latency_ms_mean"], label="95. percentyl opóźnień [ms]", color="tab:orange", linewidth=2)
    ax1.fill_between(
        df["Time"],
        df["p95_latency_ms_mean"] - df["p95_latency_ms_std"],
        df["p95_latency_ms_mean"] + df["p95_latency_ms_std"],
        color="tab:orange",
        alpha=0.2,
        label="±1σ (p95)"
    )

    # Oś Y (lewa)
    ax1.set_xlabel("Czas", fontsize=12)
    ax1.set_ylabel("Opóźnienie [ms]", fontsize=12, color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax1.grid(True, linestyle="--", alpha=0.6)

    # Druga oś Y (prawa)
    ax2 = ax1.twinx()
    ax2.plot(df["Time"], df["requests_mean"], color="tab:green", linestyle="--", linewidth=2, label="Liczba zapytań")
    ax2.fill_between(
        df["Time"],
        df["requests_mean"] - df["requests_std"],
        df["requests_mean"] + df["requests_std"],
        color="tab:green",
        alpha=0.15,
        label="±1σ (requests)"
    )
    ax2.set_ylabel("Liczba zapytań", fontsize=12, color="tab:green")
    ax2.tick_params(axis="y", labelcolor="tab:green")

    # Legenda łączona
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.title("Średnie opóźnienie i liczba zapytań w czasie (uśrednione 3 iteracje ±1σ)", fontsize=13, weight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"✅ Wykres zapisano do: {output_path}")


def main() -> None:
    """Ładuje dane z 3 iteracji testów, uśrednia i rysuje wykres z pasmem ±1σ."""
    base = Path("data/aks")
    iterations = ["stress01", "stress02", "stress03"]
    dfs = []

    for it in iterations:
        df = load_time_series_data(
            base / it / "Total Requests (increase over 1m).csv",
            base / it / "95th Percentile Latency (ms).csv",
            base / it / "Average Request Duration (ms).csv",
        )
        dfs.append(df)

    df_avg = average_iterations(dfs, freq="30S")
    print("\n✅ Uśrednione dane (ze std):")
    print(df_avg.head())

    plot_latency_over_time(df_avg)


if __name__ == "__main__":
    main()
