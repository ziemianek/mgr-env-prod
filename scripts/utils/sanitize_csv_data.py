from pathlib import Path
import shutil
import re

# === KONFIGURACJA ===
ROOT_DIR = Path("data")           # katalog główny z danymi
BACKUP_DIR = Path("data_backup")  # gdzie trzymać kopie
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

SEP_LINE_RE = re.compile(r'^\ufeff?\s*sep\s*=\s*.*$', re.IGNORECASE)

def clean_csv_file(path: Path):
    """Czyści pojedynczy plik CSV i zapisuje jego kopię w osobnym katalogu backup."""
    path = Path(path)
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            raw_lines = f.readlines()

        # Ścieżka do kopii bezpieczeństwa (z zachowaniem struktury katalogów)
        relative = path.relative_to(ROOT_DIR)
        backup_path = BACKUP_DIR / relative
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)

        cleaned_lines = []
        for line in raw_lines:
            probe = line.lstrip("\ufeff").rstrip("\r\n")
            if SEP_LINE_RE.match(probe):
                continue  # pomiń linie 'sep=...'
            line = line.replace("\ufeff", "").replace('"', "").replace("'", "")
            cleaned_lines.append(line)

        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.writelines(cleaned_lines)

        print(f"✅ Wyczyściłem: {relative}")

    except Exception as e:
        print(f"⚠️ Błąd przy {path}: {e}")


def clean_all_csvs(root: Path):
    """Rekurencyjnie czyści wszystkie pliki CSV w katalogu root."""
    csv_files = list(Path(root).rglob("*.csv"))
    print(f"🔍 Znaleziono {len(csv_files)} plików CSV w katalogu {root.resolve()}")
    for csv_path in csv_files:
        clean_csv_file(csv_path)
    print(f"🎯 Czyszczenie zakończone. Kopie zapisano w: {BACKUP_DIR.resolve()}")


if __name__ == "__main__":
    clean_all_csvs(ROOT_DIR)
