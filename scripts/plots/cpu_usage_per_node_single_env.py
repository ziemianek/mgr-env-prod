import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from pathlib import Path

# === KONFIGURACJA ===
BASE_DIR = Path("data/gke")
OUT_DIR = Path("results/gke_stress_cpu_nodes")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Moment rozpoczęcia testów (na podstawie logów K6)
T0_MAP = {
    "stress01": pd.Timestamp("2025-10-17 20:09:30"),
    "stress02": pd.Timestamp("2025-10-18 09:36:00"),
    "stress03": pd.Timestamp("2025-10-18 8:51:00"),
}

def load_cpu_node_csv(path):
    """Wczytaj CSV z metryką CPU Utilisation i oczyść dane."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    # Znajdź linię z nagłówkiem
    start_idx = 0
    for i, line in enumerate(lines):
        if "Time" in line:
            start_idx = i
            break
    sep = ";" if ";" in lines[start_idx] else ","
    df = pd.read_csv(path, skiprows=start_idx, sep=sep)
    df = df.dropna(axis=1, how="all")
    if "Time" not in df.columns:
        raise ValueError(f"Brak kolumny 'Time' w {path}")
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    df = df.dropna(subset=["Time"]).set_index("Time")
    df["Utilisation"] = (
        df["Utilisation"].astype(str)
        .str.replace("%", "", regex=False)
        .replace("", None)
        .astype(float)
    )
    return df


def align_to_t0(df, t0_test):
    """Przesuń oś czasu względem momentu startu testu, zachowując baseline."""
    df = df.copy()
    df.index = (df.index - t0_test).total_seconds() / 60.0  # w minutach
    df.index.name = "Minutes since test start"
    return df  # nie odcinamy już baseline'u


def load_all_nodes_for_all_tests():
    """Wczytaj dane CPU dla wszystkich node’ów i testów."""
    all_data = {}
    for test_name, t0_test in T0_MAP.items():
        test_dir = BASE_DIR / test_name
        node_dirs = [d for d in test_dir.glob("node-*") if d.is_dir()]
        for node in node_dirs:
            cpu_file = next(node.glob("CPU Utilisation*.csv"), None)
            if cpu_file:
                df = load_cpu_node_csv(cpu_file)
                df = align_to_t0(df, t0_test)
                # Nadaj unikalny identyfikator node'a
                label = f"{node.name} ({test_name})"
                all_data[label] = df
    return all_data

import matplotlib.pyplot as plt
import itertools

def plot_all_nodes(all_data):
    """
    Rysuje zużycie CPU dla wszystkich node'ów z trzech testów stress.
    Zawiera oznaczenie baseline, okresu testu i polskie etykiety.
    """
    plt.figure(figsize=(12, 6))
    plt.style.use("default")  # białe tło wykresu

    # === paleta kolorów (podobne odcienie dla każdej iteracji testu) ===
    # 3 testy × 2 node'y = 6 kolorów z trzech zbliżonych gam
    color_groups = [
        ["#1f77b4", "#2ca02c"],  # odcienie niebiesko-zielone (stress01)
        ["#d62728", "#ff7f0e"],  # czerwono-pomarańczowe (stress02)
        ["#9467bd", "#8c564b"],  # fioletowo-brązowe (stress03)
    ]
    colors = list(itertools.chain.from_iterable(color_groups))

    # === skrócone etykiety dla legendy ===
    label_map = {
        "node-10-10-0-3": "node1",
        "node-10-10-0-4": "node1",
        "node-10-10-0-5": "node2",
    }

    # === rysowanie linii ===
    for i, (label, df) in enumerate(all_data.items()):
        # Wyodrębnij nazwę testu (np. stress01) i nazwę node'a
        parts = label.replace("(", "").replace(")", "").split()
        node_ip = parts[0]
        test_name = parts[-1]
        short_label = f"{label_map.get(node_ip, node_ip)} ({test_name})"
        plt.plot(df.index, df["Utilisation"], lw=2, color=colors[i % len(colors)], label=short_label)

    # === podświetlenie baseline i okresu testu ===
    # plt.axvspan(-5, 0, color="#a7c7e7", alpha=0.25, label="okres bazowy (baseline)")
    plt.axvspan(0, 10, color="lightgray", alpha=0.3, label="okres trwania testu")

    # === pionowe linie dla startu i końca testu (ten sam kolor) ===
    plt.axvline(0, color="#2b8cbe", linestyle="--", lw=1.5, label="początek i koniec testu")
    plt.axvline(10, color="#2b8cbe", linestyle="--", lw=1.5)

    # === formatowanie osi i tytułów ===
    plt.title("Zużycie CPU na poziomie węzłów w klastrze GKE (testy stresowe 01–03)", fontsize=13)
    plt.xlabel("Czas od rozpoczęcia testu [minuty]", fontsize=11)
    plt.ylabel("Zużycie CPU [%]", fontsize=11)
    plt.xlim(-5, 20)
    plt.grid(True, alpha=0.4)

    # >>> WYMIUSZONE ODSTĘPY CO 1 MINUTE <<<
    plt.gca().xaxis.set_major_locator(MultipleLocator(1))
    plt.xticks(rotation=0)  # zachowaj poziome etykiety
    plt.minorticks_off()    # wyłącz drobne znaczniki, jeśli niepotrzebne

    plt.legend(fontsize=9, loc="upper right", ncol=2)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "gke_all_stress_cpu_nodes_final.png", dpi=200)
    plt.close()



# === GŁÓWNY BLOK ===
print("📊 Wczytywanie danych dla wszystkich testów...")
all_data = load_all_nodes_for_all_tests()
plot_all_nodes(all_data)
print(f"✅ Wykres zapisano w: {OUT_DIR / 'gke_all_stress_cpu_nodes.png'}")
