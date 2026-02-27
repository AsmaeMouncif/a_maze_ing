import random
import time
import sys
import os
from collections import deque

RESET  = "\033[0m"
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
#  Config loader  (strict — no defaults)
# ─────────────────────────────────────────────

CONFIG_PATH   = "config.txt"
MIN_SIZE      = 5
MAX_SIZE      = 99
REQUIRED_KEYS = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")


def _make_odd(n):
    return n if n % 2 == 1 else n + 1


def _err(msg):
    print(f"\033[91m[ERROR] {msg}\033[0m")


def load_config(path=CONFIG_PATH):
    """
    Read config.txt and return a validated config dict, or None on any error.

    Required keys:
        WIDTH       - integer 5-99
        HEIGHT      - integer 5-99
        ENTRY       - "col,row" on the border  e.g. ENTRY=0,1
        EXIT        - "col,row" on the border  e.g. EXIT=40,23
        OUTPUT_FILE - non-empty string          e.g. OUTPUT_FILE=maze.txt
        PERFECT     - True or False

    Returns None (and prints a clear error) on any problem — no fallback defaults.
    """
    # 1. File existence
    if not os.path.exists(path):
        _err(f"Config file '{path}' not found. Please create it before running.")
        return None

    # 2. Parse key=value pairs
    raw = {}
    try:
        with open(path, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    _err(f"config.txt line {line_num}: invalid format '{line}' "
                         f"(expected KEY=VALUE).")
                    return None
                key, _, value = line.partition("=")
                raw[key.strip().upper()] = value.strip()
    except OSError as e:
        _err(f"Cannot read '{path}': {e}")
        return None

    # 3. All required keys present
    for key in REQUIRED_KEYS:
        if key not in raw:
            _err(f"Missing required key '{key}' in config.txt.")
            return None

    # 4. WIDTH
    if not raw["WIDTH"].lstrip("-").isdigit():
        _err(f"Invalid WIDTH value '{raw['WIDTH']}': must be an integer (e.g. WIDTH=40).")
        return None
    cols = int(raw["WIDTH"])
    if cols < MIN_SIZE:
        _err(f"WIDTH={cols} is too small (minimum {MIN_SIZE}).")
        return None
    if cols > MAX_SIZE:
        _err(f"WIDTH={cols} is too large (maximum {MAX_SIZE}).")
        return None
    cols = _make_odd(cols)

    # 5. HEIGHT
    if not raw["HEIGHT"].lstrip("-").isdigit():
        _err(f"Invalid HEIGHT value '{raw['HEIGHT']}': must be an integer (e.g. HEIGHT=25).")
        return None
    rows = int(raw["HEIGHT"])
    if rows < MIN_SIZE:
        _err(f"HEIGHT={rows} is too small (minimum {MIN_SIZE}).")
        return None
    if rows > MAX_SIZE:
        _err(f"HEIGHT={rows} is too large (maximum {MAX_SIZE}).")
        return None
    rows = _make_odd(rows)

    # 6. ENTRY  "col,row"
    entry_parts = raw["ENTRY"].split(",")
    if len(entry_parts) != 2 or not all(p.strip().lstrip("-").isdigit() for p in entry_parts):
        _err(f"Invalid ENTRY value '{raw['ENTRY']}': "
             f"must be two integers separated by a comma (e.g. ENTRY=0,1).")
        return None
    entry_col, entry_row = int(entry_parts[0].strip()), int(entry_parts[1].strip())
    if not (0 <= entry_col < cols and 0 <= entry_row < rows):
        _err(f"ENTRY={entry_col},{entry_row} is out of bounds "
             f"for a {cols}x{rows} maze (cols 0-{cols-1}, rows 0-{rows-1}).")
        return None
    if not (entry_row == 0 or entry_row == rows - 1
            or entry_col == 0 or entry_col == cols - 1):
        _err(f"ENTRY={entry_col},{entry_row} must be on the border of the maze "
             f"(row 0, row {rows-1}, col 0, or col {cols-1}).")
        return None

    # 7. EXIT  "col,row"
    exit_parts = raw["EXIT"].split(",")
    if len(exit_parts) != 2 or not all(p.strip().lstrip("-").isdigit() for p in exit_parts):
        _err(f"Invalid EXIT value '{raw['EXIT']}': "
             f"must be two integers separated by a comma (e.g. EXIT=40,23).")
        return None
    exit_col, exit_row = int(exit_parts[0].strip()), int(exit_parts[1].strip())
    if not (0 <= exit_col < cols and 0 <= exit_row < rows):
        _err(f"EXIT={exit_col},{exit_row} is out of bounds "
             f"for a {cols}x{rows} maze (cols 0-{cols-1}, rows 0-{rows-1}).")
        return None
    if not (exit_row == 0 or exit_row == rows - 1
            or exit_col == 0 or exit_col == cols - 1):
        _err(f"EXIT={exit_col},{exit_row} must be on the border of the maze "
             f"(row 0, row {rows-1}, col 0, or col {cols-1}).")
        return None

    if (entry_col, entry_row) == (exit_col, exit_row):
        _err("ENTRY and EXIT must not be the same cell.")
        return None

    # 8. OUTPUT_FILE
    if not raw["OUTPUT_FILE"]:
        _err("OUTPUT_FILE must not be empty (e.g. OUTPUT_FILE=maze.txt).")
        return None

    # 9. PERFECT
    perfect_str = raw["PERFECT"].strip().lower()
    if perfect_str not in ("true", "false"):
        _err(f"Invalid PERFECT value '{raw['PERFECT']}': must be True or False.")
        return None
    perfect = (perfect_str == "true")

    return {
        "rows":        rows,
        "cols":        cols,
        "entry":       (entry_row, entry_col),   # stored as (r, c) internally
        "exit":        (exit_row,  exit_col),
        "output_file": raw["OUTPUT_FILE"],
        "perfect":     perfect,
    }


# ─────────────────────────────────────────────
#  Color helpers
# ─────────────────────────────────────────────

def get_wall():
    return WALL_COLORS[current_color_index][0] + " " + RESET


def get_trace():
    return WALL_COLORS[current_color_index][1] + " " + RESET


def get_entry():
    """Entry marker: same color as trace."""
    return WALL_COLORS[current_color_index][1] + " " + RESET


def get_exit():
    """Exit marker: same color as trace."""
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
#  Maze generation
# ─────────────────────────────────────────────

def _interior_neighbor(r, c, rows, cols):
    """Return the single interior cell adjacent to border cell (r, c)."""
    if r == 0:          return (1, c)
    if r == rows - 1:   return (rows - 2, c)
    if c == 0:          return (r, 1)
    if c == cols - 1:   return (r, cols - 2)
    return (r, c)  # fallback, should never reach here for a border cell


def generate_maze(rows=21, cols=21, entry=None, exit_=None):
    """
    Generate a perfect maze.

    rows / cols  - odd integers >= 5.
    entry        - (row, col) of the Entry cell on the border.
                   Defaults to (1, 0) — left wall, second row.
    exit_        - (row, col) of the Exit cell on the border.
                   Defaults to (rows-2, cols-1) — right wall, second-to-last row.

    The chosen border cells are set to 'E' / 'X' and their adjacent
    interior cells are forced open so the BFS solver can always reach them.
    """
    if entry is None:
        entry = (1, 0)
    if exit_ is None:
        exit_ = (rows - 2, cols - 1)

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

    # Place ENTRY — open its interior neighbour if it's still a wall
    er, ec = entry
    maze[er][ec] = 'E'
    ir, ic = _interior_neighbor(er, ec, rows, cols)
    if maze[ir][ic] == 'W':
        maze[ir][ic] = ' '

    # Place EXIT — same
    xr, xc = exit_
    maze[xr][xc] = 'X'
    ir, ic = _interior_neighbor(xr, xc, rows, cols)
    if maze[ir][ic] == 'W':
        maze[ir][ic] = ' '

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
        path = queue.popleft()
        r, c = path[-1]

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

def display_maze(maze, show_path=False, path=None):
    cols     = len(maze[0])
    wall     = get_wall()
    trace    = get_trace()
    entry    = get_entry()
    exit_    = get_exit()
    path_set = set(path) if path else set()

    print(BORDER * (cols + 2))
    for r, row in enumerate(maze):
        line = BORDER
        for c, cell in enumerate(row):
            if cell == 'E':
                line += entry
            elif cell == 'X':
                line += exit_
            elif show_path and (r, c) in path_set:
                line += trace
            elif cell == 'W':
                line += wall
            else:
                line += PATH
        line += BORDER
        print(line)
    print(BORDER * (cols + 2))


def animate_path(maze, path, delay=0.03, stop_event=None):
    """Animate the solution path cell by cell using absolute cursor positioning."""
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