#!/usr/bin/env python3

import pathlib
import re
import shutil

from logger import *


ROOT_DIR = pathlib.Path("data")
BACKUP_DIR = pathlib.Path("data_backup")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
SEP_LINE_RE = re.compile(r'^\ufeff?\s*sep\s*=\s*.*$', re.IGNORECASE)


def clean_csv_file(path: pathlib.Path) -> None:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            raw_lines = f.readlines()
        relative = path.relative_to(ROOT_DIR)
        backup_path = BACKUP_DIR / relative
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
        cleaned_lines = []
        for line in raw_lines:
            probe = line.lstrip("\ufeff").rstrip("\r\n")
            if SEP_LINE_RE.match(probe):
                continue  # skip line 'sep=...'
            line = line.replace("\ufeff", "").replace('"', "").replace("'", "")
            cleaned_lines.append(line)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.writelines(cleaned_lines)
        print_debug(f"Cleaned up file: {relative}")
    except Exception as e:
        print_error(f"Could not clean up {path}: {e}")


def clean_all_csvs(root: pathlib.Path) -> None:
    csv_files = list(pathlib.Path(root).rglob("*.csv"))
    print_debug(f"Found {len(csv_files)} files in {root.resolve()}")
    for csv_path in csv_files:
        clean_csv_file(csv_path)
    print_debug(f"Clean up done. Copies saved to: {BACKUP_DIR.resolve()}")


def main():
    clean_all_csvs(ROOT_DIR)


if __name__ == "__main__":
    main()
    