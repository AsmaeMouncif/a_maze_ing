import sys
import time
from threading import Event
from typing import Optional

from visual.colors import BORDER, PATH, get_wall, get_trace, get_entry, get_exit
from visual.terminal import check_terminal_size

MAZE_TOP_ROW: int = 1


def animate_generation(
    maze: list[list[str]],
    carve_steps: list[tuple[int, int]],
    delay: float = 0.007,
    stop_event: Optional[Event] = None,
    logo_cells: Optional[set[tuple[int, int]]] = None,
) -> None:
    rows = len(maze)
    if rows > 0:
        cols = len(maze[0])
    else:
        cols = 0
    check_terminal_size(rows, cols)

    wall = get_wall()
    e_ch = get_entry()
    x_ch = get_exit()
    trace = get_trace()
    if logo_cells is not None:
        _logo = logo_cells
    else:
        _logo = set()

    sys.stdout.write("\033[2J\033[H")
    print(BORDER * (cols + 2))
    for r, row in enumerate(maze):
        line = BORDER
        for c, cell in enumerate(row):
            if cell == 'E':
                line += e_ch
            elif cell == 'X':
                line += x_ch
            elif r % 2 == 1 and c % 2 == 1:
                line += trace
            else:
                line += wall
        line += BORDER
        print(line)
    print(BORDER * (cols + 2))
    sys.stdout.flush()
    time.sleep(0.3)

    carved_set: set[tuple[int, int]] = set(carve_steps)
    for r, c in carve_steps:
        if stop_event is not None:
            if stop_event.is_set():
                return
        if (r, c) in _logo:
            continue
        cell = maze[r][c]
        if cell == 'E':
            char = e_ch
        elif cell == 'X':
            char = x_ch
        else:
            char = PATH
        term_row = MAZE_TOP_ROW + 1 + r
        term_col = c * 2 + 3
        sys.stdout.write(f"\033[s\033[{term_row};{term_col}f{char}\033[u")
        sys.stdout.flush()
        time.sleep(delay)

    remaining = [
        (r, c)
        for r in range(1, rows - 1)
        for c in range(1, cols - 1)
        if r % 2 == 1 and c % 2 == 1
        and (r, c) not in carved_set
        and (r, c) not in _logo
    ]
    cr, cc = rows // 2, cols // 2
    remaining.sort(key=lambda rc: abs(rc[0] - cr) + abs(rc[1] - cc))

    for r, c in remaining:
        if stop_event is not None and stop_event.is_set():
            return
        term_row = MAZE_TOP_ROW + 1 + r
        term_col = c * 2 + 3
        sys.stdout.write(f"\033[s\033[{term_row};{term_col}f{wall}\033[u")
        sys.stdout.flush()
        time.sleep(0.002)


def animate_path(
    maze: list[list[str]],
    path: list[tuple[int, int]],
    delay: float = 0.03,
    stop_event: Optional[Event] = None,
) -> None:
    trace = get_trace()
    for r, c in path:
        if stop_event is not None and stop_event.is_set():
            return
        if maze[r][c] == 'W':
            continue
        term_row = MAZE_TOP_ROW + 1 + r
        term_col = c * 2 + 3
        sys.stdout.write(f"\033[s\033[{term_row};{term_col}f{trace}\033[u")
        sys.stdout.flush()
        time.sleep(delay)
