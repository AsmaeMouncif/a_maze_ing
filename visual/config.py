import os
from typing import Optional


CONFIG_PATH: str = "config.txt"
MIN_SIZE: int = 5
MAX_SIZE: int = 99
REQUIRED_KEYS: tuple[str, ...] = (
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
)


def _make_odd(n: int) -> int:
    return n if n % 2 == 1 else n + 1


def _err(msg: str) -> None:
    print(f"\033[91m[ERROR] {msg}\033[0m")


def load_config(path: str = CONFIG_PATH) -> Optional[dict]:
    if not os.path.exists(path):
        _err(f"Config file '{path}' not found.")
        return None

    raw: dict[str, str] = {}
    try:
        with open(path, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    _err(
                        f"Line {line_num}: invalid format '{line}' "
                        f"(expected KEY=VALUE)."
                    )
                    return None
                key, _, value = line.partition("=")
                raw[key.strip().upper()] = value.strip()
    except OSError as e:
        _err(f"Cannot read '{path}': {e}")
        return None

    for key in REQUIRED_KEYS:
        if key not in raw:
            _err(f"Missing required key '{key}' in config file.")
            return None

    if not raw["WIDTH"].lstrip("-").isdigit():
        _err(f"Invalid WIDTH '{raw['WIDTH']}': must be an integer.")
        return None
    cols_raw = int(raw["WIDTH"])
    if not (MIN_SIZE <= cols_raw <= MAX_SIZE):
        _err(f"WIDTH={cols_raw} out of range ({MIN_SIZE}-{MAX_SIZE}).")
        return None

    if not raw["HEIGHT"].lstrip("-").isdigit():
        _err(f"Invalid HEIGHT '{raw['HEIGHT']}': must be an integer.")
        return None
    rows_raw = int(raw["HEIGHT"])
    if not (MIN_SIZE <= rows_raw <= MAX_SIZE):
        _err(f"HEIGHT={rows_raw} out of range ({MIN_SIZE}-{MAX_SIZE}).")
        return None

    entry_parts = raw["ENTRY"].split(",")
    if (
        len(entry_parts) != 2
        or not all(p.strip().lstrip("-").isdigit() for p in entry_parts)
    ):
        _err(
            f"Invalid ENTRY '{raw['ENTRY']}': expected col,row "
            f"(e.g. ENTRY=0,0)."
        )
        return None
    entry_col = int(entry_parts[0].strip())
    entry_row = int(entry_parts[1].strip())
    if not (0 <= entry_col < cols_raw and 0 <= entry_row < rows_raw):
        _err(f"ENTRY={entry_col},{entry_row} is out of bounds.")
        return None
    if not (
        entry_row == 0
        or entry_row == rows_raw - 1
        or entry_col == 0
        or entry_col == cols_raw - 1
    ):
        _err(f"ENTRY={entry_col},{entry_row} must be on the border.")
        return None

    exit_parts = raw["EXIT"].split(",")
    if (
        len(exit_parts) != 2
        or not all(p.strip().lstrip("-").isdigit() for p in exit_parts)
    ):
        _err(
            f"Invalid EXIT '{raw['EXIT']}': expected col,row "
            f"(e.g. EXIT=19,14)."
        )
        return None
    exit_col = int(exit_parts[0].strip())
    exit_row = int(exit_parts[1].strip())
    if not (0 <= exit_col < cols_raw and 0 <= exit_row < rows_raw):
        _err(f"EXIT={exit_col},{exit_row} is out of bounds.")
        return None
    if not (
        exit_row == 0
        or exit_row == rows_raw - 1
        or exit_col == 0
        or exit_col == cols_raw - 1
    ):
        _err(f"EXIT={exit_col},{exit_row} must be on the border.")
        return None

    if (entry_col, entry_row) == (exit_col, exit_row):
        _err("ENTRY and EXIT must not be the same cell.")
        return None

    cols = _make_odd(cols_raw)
    rows = _make_odd(rows_raw)

    if entry_col == cols_raw - 1:
        entry_col = cols - 1
    if entry_row == rows_raw - 1:
        entry_row = rows - 1
    if exit_col == cols_raw - 1:
        exit_col = cols - 1
    if exit_row == rows_raw - 1:
        exit_row = rows - 1

    if not raw["OUTPUT_FILE"]:
        _err("OUTPUT_FILE must not be empty.")
        return None

    perfect_str = raw["PERFECT"].strip().lower()
    if perfect_str not in ("true", "false"):
        _err(f"Invalid PERFECT '{raw['PERFECT']}': must be True or False.")
        return None
    perfect = perfect_str == "true"

    seed: Optional[int] = None
    if "SEED" in raw:
        if not raw["SEED"].lstrip("-").isdigit():
            _err(f"Invalid SEED '{raw['SEED']}': must be an integer.")
            return None
        seed = int(raw["SEED"])

    return {
        "rows":        rows,
        "cols":        cols,
        "entry":       (entry_row, entry_col),
        "exit":        (exit_row, exit_col),
        "output_file": raw["OUTPUT_FILE"],
        "perfect":     perfect,
        "seed":        seed,
    }
