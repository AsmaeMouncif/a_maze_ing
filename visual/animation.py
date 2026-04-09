"""Animation module for maze generation and solution path display.

This module provides the bonus animation feature: it reveals maze cells
one by one as they are carved during generation, giving a real-time
visual of the recursive backtracker algorithm at work.
"""

import sys
import time
from threading import Event
from typing import Optional

from visual.colors import (
    BORDER,
    PATH,
    get_wall,
    get_trace,
    get_entry,
    get_exit,
)
from visual.terminal import check_terminal_size

MAZE_TOP_ROW: int = 1


def animate_generation(
    maze: list[list[str]],
    carve_steps: list[tuple[int, int]],
    delay: float = 0.007,
    stop_event: Optional[Event] = None,
    logo_cells: Optional[set[tuple[int, int]]] = None,
) -> None:
    """Animate the maze generation process step by step in the terminal.

    First draws the maze fully walled, then progressively reveals each
    carved cell in the order they were carved, producing a real-time
    animation of the generation algorithm.

    Args:
        maze: Final 2D grid of characters representing the maze.
        carve_steps: Ordered list of (row, col) positions carved during
            generation. Each position is revealed with a short delay.
        delay: Time in seconds to wait between each carved cell reveal.
            Defaults to 0.007 seconds.
        stop_event: Optional threading Event. When set, the animation
            stops immediately at the next iteration.
        logo_cells: Set of (row, col) positions reserved for the '42'
            logo. These cells are skipped during the animation.
    """
    rows = len(maze)
    cols = len(maze[0]) if rows > 0 else 0
    check_terminal_size(rows, cols)

    wall = get_wall()
    e_ch = get_entry()
    x_ch = get_exit()
    trace = get_trace()
    _logo: set[tuple[int, int]] = (
        logo_cells if logo_cells is not None else set()
    )

    try:
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
            if stop_event is not None and stop_event.is_set():
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
            sys.stdout.write(
                f"\033[s\033[{term_row};{term_col}f{char}\033[u"
            )
            sys.stdout.flush()
            time.sleep(delay)

        remaining: list[tuple[int, int]] = [
            (r, c)
            for r in range(1, rows - 1)
            for c in range(1, cols - 1)
            if r % 2 == 1
            and c % 2 == 1
            and (r, c) not in carved_set
            and (r, c) not in _logo
        ]
        cr, cc = rows // 2, cols // 2
        remaining.sort(
            key=lambda rc: abs(rc[0] - cr) + abs(rc[1] - cc)
        )

        for r, c in remaining:
            if stop_event is not None and stop_event.is_set():
                return
            term_row = MAZE_TOP_ROW + 1 + r
            term_col = c * 2 + 3
            sys.stdout.write(
                f"\033[s\033[{term_row};{term_col}f{wall}\033[u"
            )
            sys.stdout.flush()
            time.sleep(0.002)

    except OSError as e:
        print(f"\033[91m[ERROR] Terminal write error: {e}\033[0m")


def animate_path(
    maze: list[list[str]],
    path: list[tuple[int, int]],
    delay: float = 0.20,
    stop_event: Optional[Event] = None,
) -> None:
    """Animate the solution path through the maze cell by cell.

    Highlights each cell of the solution path in sequence, producing a
    smooth reveal of the route from entry to exit.

    Args:
        maze: 2D grid of characters representing the maze state.
        path: Ordered list of (row, col) positions forming the solution.
        delay: Time in seconds to wait between each cell highlight.
            Defaults to 0.03 seconds.
        stop_event: Optional threading Event. When set, the animation
            stops immediately at the next iteration.
    """
    trace = get_trace()
    try:
        for r, c in path:
            if stop_event is not None and stop_event.is_set():
                return
            if maze[r][c] == 'W':
                continue
            term_row = MAZE_TOP_ROW + 1 + r
            term_col = c * 2 + 3
            sys.stdout.write(
                f"\033[s\033[{term_row};{term_col}f{trace}\033[u"
            )
            sys.stdout.flush()
            time.sleep(delay)
    except OSError as e:
        print(f"\033[91m[ERROR] Terminal write error: {e}\033[0m")
