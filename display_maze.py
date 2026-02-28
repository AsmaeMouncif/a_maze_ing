"""
display_maze.py — Visual representation module for A-Maze-ing.

Handles:
- Config file loading and validation
- Terminal rendering with ANSI colors
- Solution path animation
- Wall color rotation

Maze generation is handled by maze_generator.py (MazeGenerator class).
"""

import sys
import os
import time
from typing import Optional

RESET: str = "\033[0m"
PATH: str = "\033[48;5;232m" + "  " + RESET
BORDER: str = "  "

WALL_COLORS: list[tuple[str, str, str, str]] = [
    ("\033[47m",        "\033[100m",       "White",        "Gray"),
    ("\033[107m",       "\033[100m",       "Bright White", "Gray"),
    ("\033[48;5;20m",   "\033[48;5;153m",  "Blue",         "Light Blue"),
    ("\033[48;5;37m",   "\033[48;5;159m",  "Cyan",         "Light Cyan"),
    ("\033[48;5;28m",   "\033[48;5;121m",  "Green",        "Light Green"),
    ("\033[48;5;130m",  "\033[48;5;223m",  "Gold",         "Light Peach"),
    ("\033[48;5;91m",   "\033[48;5;219m",  "Purple",       "Light Pink"),
    ("\033[48;5;124m",  "\033[48;5;217m",  "Dark Red",     "Light Salmon"),
]

current_color_index: int = 0
MAZE_TOP_ROW: int = 1

CONFIG_PATH: str = "config.txt"
MIN_SIZE: int = 5
MAX_SIZE: int = 99
REQUIRED_KEYS: tuple[str, ...] = (
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
)


# ─────────────────────────────────────────────
#  Config loader
# ─────────────────────────────────────────────

def _make_odd(n: int) -> int:
    """Return n if odd, else n + 1."""
    return n if n % 2 == 1 else n + 1


def _err(msg: str) -> None:
    """Print a red formatted error message."""
    print(f"\033[91m[ERROR] {msg}\033[0m")


def load_config(path: str = CONFIG_PATH) -> Optional[dict]:  # type: ignore[type-arg]
    """
    Read and validate the configuration file.

    Args:
        path: Path to the config file (default: 'config.txt').

    Returns:
        Dict with keys: rows, cols, entry, exit, output_file, perfect, seed.
        Returns None and prints an error if any validation fails.
    """
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
                    _err(f"Line {line_num}: invalid format '{line}' (expected KEY=VALUE).")
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
    cols = int(raw["WIDTH"])
    if not (MIN_SIZE <= cols <= MAX_SIZE):
        _err(f"WIDTH={cols} out of range ({MIN_SIZE}-{MAX_SIZE}).")
        return None
    cols = _make_odd(cols)

    if not raw["HEIGHT"].lstrip("-").isdigit():
        _err(f"Invalid HEIGHT '{raw['HEIGHT']}': must be an integer.")
        return None
    rows = int(raw["HEIGHT"])
    if not (MIN_SIZE <= rows <= MAX_SIZE):
        _err(f"HEIGHT={rows} out of range ({MIN_SIZE}-{MAX_SIZE}).")
        return None
    rows = _make_odd(rows)

    entry_parts = raw["ENTRY"].split(",")
    if (len(entry_parts) != 2
            or not all(p.strip().lstrip("-").isdigit() for p in entry_parts)):
        _err(f"Invalid ENTRY '{raw['ENTRY']}': expected col,row (e.g. ENTRY=0,0).")
        return None
    entry_col = int(entry_parts[0].strip())
    entry_row = int(entry_parts[1].strip())
    if not (0 <= entry_col < cols and 0 <= entry_row < rows):
        _err(f"ENTRY={entry_col},{entry_row} is out of bounds.")
        return None
    if not (entry_row == 0 or entry_row == rows - 1
            or entry_col == 0 or entry_col == cols - 1):
        _err(f"ENTRY={entry_col},{entry_row} must be on the border.")
        return None

    exit_parts = raw["EXIT"].split(",")
    if (len(exit_parts) != 2
            or not all(p.strip().lstrip("-").isdigit() for p in exit_parts)):
        _err(f"Invalid EXIT '{raw['EXIT']}': expected col,row (e.g. EXIT=19,14).")
        return None
    exit_col = int(exit_parts[0].strip())
    exit_row = int(exit_parts[1].strip())
    if not (0 <= exit_col < cols and 0 <= exit_row < rows):
        _err(f"EXIT={exit_col},{exit_row} is out of bounds.")
        return None
    if not (exit_row == 0 or exit_row == rows - 1
            or exit_col == 0 or exit_col == cols - 1):
        _err(f"EXIT={exit_col},{exit_row} must be on the border.")
        return None

    if (entry_col, entry_row) == (exit_col, exit_row):
        _err("ENTRY and EXIT must not be the same cell.")
        return None

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


# ─────────────────────────────────────────────
#  Color helpers
# ─────────────────────────────────────────────

def get_wall() -> str:
    """Return ANSI wall character with current color."""
    return WALL_COLORS[current_color_index][0] + "  " + RESET


def get_trace() -> str:
    """Return ANSI path trace character with current color."""
    return WALL_COLORS[current_color_index][1] + "  " + RESET


def get_entry() -> str:
    """Return ANSI entry marker character (same color as path trace)."""
    return get_trace()


def get_exit() -> str:
    """Return ANSI exit marker character (same color as path trace)."""
    return get_trace()


def rotate_wall_color() -> None:
    """Cycle to the next wall/trace color scheme and print its name."""
    global current_color_index
    current_color_index = (current_color_index + 1) % len(WALL_COLORS)
    name_wall = WALL_COLORS[current_color_index][2]
    name_trace = WALL_COLORS[current_color_index][3]
    print(f"\033[96m[Color] {name_wall} / {name_trace}\033[0m")


# ─────────────────────────────────────────────
#  Terminal helpers
# ─────────────────────────────────────────────

def clear_maze_display() -> None:
    """Clear the terminal screen and move cursor to top-left."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


# ─────────────────────────────────────────────
#  Rendering
# ─────────────────────────────────────────────

def display_maze(
    maze: list[list[str]],
    show_path: bool = False,
    path: Optional[list[tuple[int, int]]] = None
) -> None:
    """
    Render the maze to the terminal using ANSI color blocks.

    Args:
        maze:      2D grid ('W'=wall, ' '=open, 'E'=entry, 'X'=exit).
        show_path: If True, highlight the solution path cells.
        path:      List of (row, col) tuples for the solution path.
    """
    cols = len(maze[0])
    wall = get_wall()
    trace = get_trace()
    entry_ch = get_entry()
    exit_ch = get_exit()
    path_set: set[tuple[int, int]] = set(path) if path else set()

    print(BORDER * (cols + 2))
    for r, row in enumerate(maze):
        line = BORDER
        for c, cell in enumerate(row):
            if cell == 'E':
                line += entry_ch
            elif cell == 'X':
                line += exit_ch
            elif show_path and (r, c) in path_set:
                line += trace
            elif cell == 'W':
                line += wall
            else:
                line += PATH
        line += BORDER
        print(line)
    print(BORDER * (cols + 2))


def animate_generation(
    maze: list[list[str]],
    carve_steps: list[tuple[int, int]],
    delay: float = 0.008,
    stop_event: object = None,
) -> None:
    """
    Animate the maze being carved from a full-wall grid, cell by cell.

    Starts by displaying a fully-walled maze, then progressively reveals
    each opened cell using absolute cursor positioning.

    Args:
        maze:        The final maze grid (used to identify entry/exit).
        carve_steps: Ordered (row, col) cells opened during generation.
        delay:       Seconds between each carved cell reveal.
        stop_event:  threading.Event — stops animation immediately when set.
    """
    rows = len(maze)
    cols = len(maze[0]) if rows else 0
    wall = get_wall()
    path_ch = PATH
    entry_ch = get_entry()
    exit_ch = get_exit()

    # Draw fully-walled starting state
    sys.stdout.write("\033[2J\033[H")
    print(BORDER * (cols + 2))
    for r in range(rows):
        line = BORDER
        for c in range(cols):
            cell = maze[r][c]
            if cell == 'E':
                line += wall
            elif cell == 'X':
                line += wall
            else:
                line += wall
        line += BORDER
        print(line)
    print(BORDER * (cols + 2))
    sys.stdout.flush()

    # Reveal carved cells one by one
    for r, c in carve_steps:
        if stop_event is not None and stop_event.is_set():  # type: ignore[attr-defined]
            return
        cell = maze[r][c]
        if cell == 'E':
            char = entry_ch
        elif cell == 'X':
            char = exit_ch
        else:
            char = path_ch
        term_row = MAZE_TOP_ROW + 1 + r
        term_col = c * 2 + 3
        sys.stdout.write(f"\033[s\033[{term_row};{term_col}f{char}\033[u")
        sys.stdout.flush()
        time.sleep(delay)


def animate_path(
    maze: list[list[str]],
    path: list[tuple[int, int]],
    delay: float = 0.03,
    stop_event: object = None,
) -> None:
    """
    Animate the solution path cell by cell with absolute cursor positioning.

    Args:
        maze:       2D maze grid.
        path:       Ordered list of (row, col) cells to animate.
        delay:      Seconds to wait between each animated cell.
        stop_event: threading.Event — stops animation immediately when set.
    """
    trace = get_trace()

    for r, c in path:
        if stop_event is not None and stop_event.is_set():  # type: ignore[attr-defined]
            return
        if maze[r][c] == 'W':
            continue
        term_row = MAZE_TOP_ROW + 1 + r
        term_col = c * 2 + 3
        sys.stdout.write(f"\033[s\033[{term_row};{term_col}f{trace}\033[u")
        sys.stdout.flush()
        time.sleep(delay)