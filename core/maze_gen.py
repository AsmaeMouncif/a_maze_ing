"""Maze generation, pathfinding, and file output for A-Maze-ing."""

import random
from collections import deque
from typing import Optional


def _make_odd(n: int, upper: int) -> int:
    """Clamp n inside [1, upper-2] and ensure it is odd."""
    v = max(1, min(n, upper - 2))
    return v if v % 2 == 1 else (v - 1 if v > 1 else v + 1)


def _border_neighbor(
    pos: tuple[int, int], rows: int, cols: int
) -> tuple[int, int]:
    """Return the cell one step inward from a border cell."""
    r, c = pos
    if r == 0:
        return (1, c)
    if r == rows - 1:
        return (rows - 2, c)
    if c == 0:
        return (r, 1)
    return (r, cols - 2)


def _connect(
    pos: tuple[int, int], rows: int, cols: int
) -> tuple[int, int]:
    """Return the nearest odd-indexed interior cell connected to pos."""
    r, c = _border_neighbor(pos, rows, cols)
    return (_make_odd(r, rows), _make_odd(c, cols))


def _would_create_open_area(
    maze: list[list[str]],
    rows: int,
    cols: int,
    tr: int,
    tc: int,
) -> bool:
    """Check if opening (tr, tc) would create a 2x2 open block.

    Preventing 2x2 open areas automatically prevents all larger open
    areas (3x3, 4x4, etc.).

    Args:
        maze: Current 2-D grid ('W' = wall).
        rows: Number of rows.
        cols: Number of columns.
        tr: Row of the candidate cell to open.
        tc: Column of the candidate cell to open.

    Returns:
        True if opening this cell would form a 2x2 open block.
    """
    original = maze[tr][tc]
    maze[tr][tc] = ' '
    found = False
    for dr in range(-1, 1):
        for dc in range(-1, 1):
            r0, c0 = tr + dr, tc + dc
            if r0 < 0 or r0 + 1 >= rows or c0 < 0 or c0 + 1 >= cols:
                continue
            if all(
                maze[r0 + i][c0 + j] != 'W'
                for i in range(2)
                for j in range(2)
            ):
                found = True
                break
        if found:
            break
    maze[tr][tc] = original
    return found


def generate_maze(
    rows: int,
    cols: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    perfect: bool,
    seed: Optional[int],
    logo_cells: set[tuple[int, int]],
) -> tuple[list[list[str]], list[tuple[int, int]]]:
    """Generate a maze using the recursive-backtracker (DFS) algorithm.

    The maze is built on an odd-indexed grid so every carved cell is
    separated by exactly one wall cell, guaranteeing a perfect maze by
    construction.  When *perfect* is False, extra passage-walls are
    removed, but only if the removal does not create a 2x2 open area.

    Logo cells are always forced back to 'W' after generation.

    Args:
        rows: Total number of rows in the grid (should be odd).
        cols: Total number of columns in the grid (should be odd).
        entry: (row, col) of the maze entrance (border cell).
        exit_: (row, col) of the maze exit (border cell).
        perfect: If True, exactly one path between any two open cells.
            If False, a small number of extra passages are added.
        seed: Random seed for reproducibility. None means random.
        logo_cells: Set of (row, col) positions reserved for the '42'
            logo; always kept as walls.

    Returns:
        A tuple (maze, steps) where *maze* is the 2-D character grid
        and *steps* is the ordered list of cells carved during
        generation (used for the generation animation).
    """
    rng = random.Random(
        seed if seed is not None else random.randint(0, 2 ** 32)
    )
    maze: list[list[str]] = [['W'] * cols for _ in range(rows)]
    steps: list[tuple[int, int]] = []

    # Phase 1 — recursive backtracker on odd-indexed cells
    start = _connect(entry, rows, cols)
    stack = [start]
    maze[start[0]][start[1]] = ' '
    steps.append(start)

    while stack:
        r, c = stack[-1]
        nbrs = []
        for dr, dc in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            nr, nc = r + dr, c + dc
            if (
                1 <= nr < rows - 1
                and 1 <= nc < cols - 1
                and maze[nr][nc] == 'W'
                and (nr, nc) not in logo_cells
            ):
                nbrs.append((nr, nc, r + dr // 2, c + dc // 2))
        if nbrs:
            nr, nc, wr, wc = rng.choice(nbrs)
            if (wr, wc) not in logo_cells:
                maze[wr][wc] = ' '
                steps.append((wr, wc))
            maze[nr][nc] = ' '
            steps.append((nr, nc))
            stack.append((nr, nc))
        else:
            stack.pop()

    # Phase 2 — open entry/exit corridors
    for cell in (
        entry,
        _border_neighbor(entry, rows, cols),
        exit_,
        _border_neighbor(exit_, rows, cols),
    ):
        r, c = cell
        if maze[r][c] == 'W':
            steps.append(cell)
        maze[r][c] = ' '

    # Phase 3 (imperfect only) — add extra passages safely
    # Only passage-walls (flanked by two open cells on opposite sides)
    # are candidates.  Any removal that would create a 2x2 open block
    # is rejected — this prevents all larger open areas too.
    if not perfect:
        candidate_walls: list[tuple[int, int]] = []
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if (r, c) in logo_cells or maze[r][c] != 'W':
                    continue
                h_open = (
                    c - 1 >= 0
                    and c + 1 < cols
                    and maze[r][c - 1] != 'W'
                    and maze[r][c + 1] != 'W'
                )
                v_open = (
                    r - 1 >= 0
                    and r + 1 < rows
                    and maze[r - 1][c] != 'W'
                    and maze[r + 1][c] != 'W'
                )
                if h_open or v_open:
                    candidate_walls.append((r, c))

        rng.shuffle(candidate_walls)
        target = max(1, (rows * cols) // 25)
        removed = 0
        for wr, wc in candidate_walls:
            if removed >= target:
                break
            if _would_create_open_area(maze, rows, cols, wr, wc):
                continue
            maze[wr][wc] = ' '
            steps.append((wr, wc))
            removed += 1

    # Phase 4 — restore logo cells
    for r, c in logo_cells:
        maze[r][c] = 'W'

    # Phase 5 — mark entry / exit
    er, ec = entry
    maze[er][ec] = 'E'
    xr, xc = exit_
    maze[xr][xc] = 'X'

    return maze, steps


def find_path(
    maze: list[list[str]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
) -> list[tuple[int, int]]:
    """Find the shortest path from entry to exit using BFS.

    Args:
        maze: 2-D character grid ('W' = wall).
        entry: Starting cell (row, col).
        exit_: Target cell (row, col).

    Returns:
        Ordered list of (row, col) positions from entry to exit,
        inclusive. Returns an empty list if no path exists.
    """
    q: deque[tuple[int, int]] = deque([entry])
    parent: dict[tuple[int, int], Optional[tuple[int, int]]] = {
        entry: None
    }

    while q:
        r, c = q.popleft()
        if (r, c) == exit_:
            break
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if not (0 <= nr < len(maze) and 0 <= nc < len(maze[0])):
                continue
            if maze[nr][nc] == 'W' or (nr, nc) in parent:
                continue
            parent[(nr, nc)] = (r, c)
            q.append((nr, nc))

    if exit_ not in parent:
        return []

    path: list[tuple[int, int]] = []
    cur: Optional[tuple[int, int]] = exit_
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path


def write_maze_file(
    maze: list[list[str]],
    path: list[tuple[int, int]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    output_file: str,
) -> None:
    """Encode the maze as hex digits and write it to a file.

    Each cell is one uppercase hex digit encoding which walls are
    closed (bit=1) or open (bit=0):

    * bit 0 (LSB) → North
    * bit 1       → East
    * bit 2       → South
    * bit 3       → West

    The entry and exit cells have their outward border wall forced open.
    After the grid rows an empty line precedes three metadata lines:
    entry coordinates, exit coordinates, and the path as N/E/S/W.

    Args:
        maze: 2-D character grid.
        path: Ordered solution path from entry to exit.
        entry: (row, col) of the entrance.
        exit_: (row, col) of the exit.
        output_file: Destination file path.
    """
    rows = len(maze)
    cols = len(maze[0])

    def _outward(pos: tuple[int, int]) -> tuple[int, int]:
        """Return the outward direction for a border cell."""
        r, c = pos
        if r == 0:
            return (-1, 0)
        if r == rows - 1:
            return (1, 0)
        if c == 0:
            return (0, -1)
        return (0, 1)

    entry_out = _outward(entry)
    exit_out = _outward(exit_)

    def is_wall(r: int, c: int, dr: int, dc: int) -> bool:
        """Return True when the wall in direction (dr, dc) is closed."""
        if maze[r][c] == 'W':
            return True    
        if (r, c) == entry and (dr, dc) == entry_out:
            return False
        if (r, c) == exit_ and (dr, dc) == exit_out:
            return False
        nr, nc = r + dr, c + dc
        if nr < 0 or nr >= rows or nc < 0 or nc >= cols:
            return True
        return maze[nr][nc] == 'W'

    lines: list[str] = []
    for r in range(rows):
        row_str = ""
        for c in range(cols):
            north = 1 if is_wall(r, c, -1, 0) else 0
            east = 1 if is_wall(r, c, 0, 1) else 0
            south = 1 if is_wall(r, c, 1, 0) else 0
            west = 1 if is_wall(r, c, 0, -1) else 0
            val = north | (east << 1) | (south << 2) | (west << 3)
            row_str += format(val, 'X')
        lines.append(row_str)

    lines.append("")
    lines.append(f"{entry[1]},{entry[0]}")
    lines.append(f"{exit_[1]},{exit_[0]}")

    direction_map: dict[tuple[int, int], str] = {
        (-1, 0): 'N',
        (1, 0): 'S',
        (0, -1): 'W',
        (0, 1): 'E',
    }
    path_str = ""
    for i in range(1, len(path)):
        dr = path[i][0] - path[i - 1][0]
        dc = path[i][1] - path[i - 1][1]
        path_str += direction_map.get((dr, dc), '?')
    lines.append(path_str)

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
    except OSError as e:
        print(
            f"\033[91m[ERROR] Cannot write to '{output_file}': {e}\033[0m"
        )
