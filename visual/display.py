"""Static maze display module for terminal rendering."""

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


def display_maze(
    maze: list[list[str]],
    show_path: bool = False,
    path: Optional[list[tuple[int, int]]] = None,
    logo_cells: Optional[set[tuple[int, int]]] = None,
) -> None:
    """Render the maze as a static image in the terminal.

    Each maze cell is drawn as a two-character block. Walls, path,
    entry, exit, and the '42' logo are rendered with distinct colors.

    Args:
        maze: 2D grid of characters representing the maze state.
            Expected cell values: 'W' (wall), ' ' (open), 'E' (entry),
            'X' (exit).
        show_path: When True, highlights the solution path cells.
        path: Ordered list of (row, col) positions forming the solution.
            Ignored when show_path is False.
        logo_cells: Set of (row, col) positions reserved for the logo.
            These cells are rendered with the wall or trace color.
    """
    rows = len(maze)
    cols = len(maze[0]) if rows > 0 else 0
    check_terminal_size(rows, cols)

    wall = get_wall()
    trace = get_trace()
    e_ch = get_entry()
    x_ch = get_exit()
    path_set: set[tuple[int, int]] = (
        set(path) if path is not None else set()
    )
    _logo: set[tuple[int, int]] = (
        logo_cells if logo_cells is not None else set()
    )

    print(BORDER * (cols + 2))
    for r, row in enumerate(maze):
        line = BORDER
        for c, cell in enumerate(row):
            if cell == 'E':
                line += e_ch
            elif cell == 'X':
                line += x_ch
            elif (r, c) in _logo:
                if r % 2 == 1 and c % 2 == 1:
                    line += trace
                else:
                    line += wall
            elif cell == 'W':
                line += wall
            elif show_path and (r, c) in path_set:
                line += trace
            else:
                line += PATH
        line += BORDER
        print(line)
    print(BORDER * (cols + 2))
