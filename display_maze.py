import random
import time
import sys
import os
from collections import deque

RESET = "\033[0m"

ENTRY  = "\033[48;5;213m" + " " + RESET
EXIT   = "\033[48;5;196m" + " " + RESET
PATH   = "\033[48;5;232m" + " " + RESET
BORDER = " "

WALL_COLORS = [
    ("\033[47m",          "\033[100m",       "White",        "Gray"),
    ("\033[107m",         "\033[100m",       "Bright White",  "Gray"),
    ("\033[48;5;20m",     "\033[48;5;153m",  "Blue",          "Light Blue"),
    ("\033[48;5;37m",     "\033[48;5;159m",  "Cyan",          "Light Cyan"),
    ("\033[48;5;28m",     "\033[48;5;121m",  "Green",         "Light Green"),
    ("\033[48;5;130m",    "\033[48;5;223m",  "Gold",          "Light Peach"),
    ("\033[48;5;91m",     "\033[48;5;219m",  "Purple",        "Light Pink"),
    ("\033[48;5;124m",    "\033[48;5;217m",  "Dark Red",      "Light Salmon"),
]

current_color_index = 0

MAZE_TOP_ROW = 1

# ─────────────────────────────────────────────
#  Config loader
# ─────────────────────────────────────────────

CONFIG_PATH = "config.txt"
CONFIG_DEFAULTS = {
    "WIDTH":  21,
    "HEIGHT": 21,
}
MIN_SIZE = 5
MAX_SIZE = 99


def _make_odd(n: int) -> int:
    """Ensure n is odd (maze algorithm needs odd dimensions)."""
    return n if n % 2 == 1 else n + 1


def load_config(path: str = CONFIG_PATH) -> dict:
    """
    Read config.txt and return validated maze dimensions.

    Returns a dict with keys 'rows' and 'cols' (always odd integers).
    Prints a clear error and falls back to defaults on any problem.
    """
    config = {}

    # ── 1. File existence ──────────────────────────────────────────────
    if not os.path.exists(path):
        print(f"\033[91m[ERROR] Config file '{path}' not found. "
              f"Using default size {CONFIG_DEFAULTS['HEIGHT']}x{CONFIG_DEFAULTS['WIDTH']}.\033[0m")
        return {
            "rows": CONFIG_DEFAULTS["HEIGHT"],
            "cols": CONFIG_DEFAULTS["WIDTH"],
        }

    # ── 2. Parse key=value pairs ───────────────────────────────────────
    try:
        with open(path, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    print(f"\033[93m[WARNING] config.txt line {line_num}: "
                          f"invalid format '{line}' (expected KEY=VALUE). Skipped.\033[0m")
                    continue
                key, _, value = line.partition("=")
                config[key.strip().upper()] = value.strip()
    except OSError as e:
        print(f"\033[91m[ERROR] Cannot read '{path}': {e}. "
              f"Using default size.\033[0m")
        return {
            "rows": CONFIG_DEFAULTS["HEIGHT"],
            "cols": CONFIG_DEFAULTS["WIDTH"],
        }

    # ── 3. Validate WIDTH ──────────────────────────────────────────────
    try:
        raw_width = config.get("WIDTH")
        if raw_width is None:
            raise KeyError("WIDTH missing from config")
        cols = int(raw_width)
        if cols < MIN_SIZE:
            raise ValueError(f"WIDTH={cols} is too small (minimum {MIN_SIZE})")
        if cols > MAX_SIZE:
            raise ValueError(f"WIDTH={cols} is too large (maximum {MAX_SIZE})")
        cols = _make_odd(cols)
    except (ValueError, KeyError) as e:
        print(f"\033[91m[ERROR] Invalid WIDTH in config: {e}. "
              f"Using default {CONFIG_DEFAULTS['WIDTH']}.\033[0m")
        cols = CONFIG_DEFAULTS["WIDTH"]

    # ── 4. Validate HEIGHT ─────────────────────────────────────────────
    try:
        raw_height = config.get("HEIGHT")
        if raw_height is None:
            raise KeyError("HEIGHT missing from config")
        rows = int(raw_height)
        if rows < MIN_SIZE:
            raise ValueError(f"HEIGHT={rows} is too small (minimum {MIN_SIZE})")
        if rows > MAX_SIZE:
            raise ValueError(f"HEIGHT={rows} is too large (maximum {MAX_SIZE})")
        rows = _make_odd(rows)
    except (ValueError, KeyError) as e:
        print(f"\033[91m[ERROR] Invalid HEIGHT in config: {e}. "
              f"Using default {CONFIG_DEFAULTS['HEIGHT']}.\033[0m")
        rows = CONFIG_DEFAULTS["HEIGHT"]

    return {"rows": rows, "cols": cols}


# ─────────────────────────────────────────────
#  Color helpers
# ─────────────────────────────────────────────

def get_wall():
    return WALL_COLORS[current_color_index][0] + " " + RESET


def get_trace():
    return WALL_COLORS[current_color_index][1] + " " + RESET


def rotate_wall_color():
    global current_color_index
    current_color_index = (current_color_index + 1) % len(WALL_COLORS)
    name_wall  = WALL_COLORS[current_color_index][2]
    name_trace = WALL_COLORS[current_color_index][3]
    print(f"\033[96m[Color] {name_wall} / {name_trace}\033[0m")


# ─────────────────────────────────────────────
#  Display helpers
# ─────────────────────────────────────────────

def clear_maze_display():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


# ─────────────────────────────────────────────
#  Maze generation  (size comes from config)
# ─────────────────────────────────────────────

def generate_maze(rows: int = 21, cols: int = 21):
    """
    Generate a perfect maze of given dimensions.
    rows and cols must be odd integers >= 5.
    Entry is on the left side, exit on the right side.
    """
    maze = [['W' for _ in range(cols)] for _ in range(rows)]

    def carve(r, c):
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and maze[nr][nc] == 'W':
                maze[r + dr // 2][c + dc // 2] = ' '
                maze[nr][nc] = ' '
                carve(nr, nc)

    maze[1][1] = ' '
    carve(1, 1)

    # Entry: left wall, row 1  |  Exit: right wall, last path row
    maze[1][0]             = 'E'
    maze[rows - 2][cols - 1] = 'X'

    return maze


# ─────────────────────────────────────────────
#  Solver
# ─────────────────────────────────────────────

def solve_maze(maze):
    rows = len(maze)
    cols = len(maze[0])

    start = end = None
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 'E':
                start = (r, c)
            elif maze[r][c] == 'X':
                end = (r, c)

    if not start or not end:
        print("\033[91m[ERROR] Could not find Entry (E) or Exit (X) in maze.\033[0m")
        return []

    queue   = deque([[start]])
    visited = {start}

    while queue:
        path     = queue.popleft()
        r, c     = path[-1]

        if (r, c) == end:
            return path

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and (nr, nc) not in visited
                    and maze[nr][nc] != 'W'):
                visited.add((nr, nc))
                queue.append(path + [(nr, nc)])

    print("\033[91m[ERROR] No path found between entry and exit.\033[0m")
    return []


# ─────────────────────────────────────────────
#  Rendering
# ─────────────────────────────────────────────

def display_maze(maze, show_path: bool = False, path=None):
    cols     = len(maze[0])
    wall     = get_wall()
    trace    = get_trace()
    path_set = set(path) if path else set()

    print(BORDER * (cols + 2))

    for r, row in enumerate(maze):
        line = BORDER
        for c, cell in enumerate(row):
            if cell == 'E':
                line += ENTRY
            elif cell == 'X':
                line += EXIT
            elif show_path and (r, c) in path_set:
                line += trace
            elif cell == 'W':
                line += wall
            else:
                line += PATH
        line += BORDER
        print(line)

    print(BORDER * (cols + 2))


def animate_path(maze, path, delay: float = 0.03, stop_event=None):
    """
    Animate the solution path cell by cell using absolute cursor positioning.

    Terminal layout (after clear_maze_display):
      row 1            : top border
      row 1 + 1 + r    : maze row r
      col c + 2        : left border offset
    """
    trace = get_trace()

    for r, c in path:
        if stop_event is not None and stop_event.is_set():
            return

        if maze[r][c] in ('E', 'X'):
            continue

        term_row = MAZE_TOP_ROW + 1 + r
        term_col = c + 2

        sys.stdout.write(f"\033[s\033[{term_row};{term_col}f{trace}\033[u")
        sys.stdout.flush()
        time.sleep(delay)