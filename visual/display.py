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
    rows = len(maze)
    cols = len(maze[0])
    check_terminal_size(rows, cols)

    wall = get_wall()
    trace = get_trace()
    e_ch = get_entry()
    x_ch = get_exit()
    if path is not None:
        path_set = set(path)
    else:
        path_set = set()
    if logo_cells is not None:
        _logo = logo_cells
    else:
        _logo = set()

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