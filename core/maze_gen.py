import random
from collections import deque
from typing import Optional


def _make_odd(n: int, upper: int) -> int:
    v = max(1, min(n, upper - 2))
    return v if v % 2 == 1 else (v - 1 if v > 1 else v + 1)


def _border_neighbor(pos: tuple[int, int],
                     rows: int, cols: int) -> tuple[int, int]:
    r, c = pos
    if r == 0:         return (1, c)
    if r == rows - 1:  return (rows - 2, c)
    if c == 0:         return (r, 1)
    return (r, cols - 2)


def _connect(pos: tuple[int, int],
             rows: int, cols: int) -> tuple[int, int]:
    r, c = _border_neighbor(pos, rows, cols)
    return (_make_odd(r, rows), _make_odd(c, cols))


def generate_maze(
    rows: int,
    cols: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    perfect: bool,
    seed: Optional[int],
    logo_cells: set[tuple[int, int]],
) -> tuple[list[list[str]], list[tuple[int, int]]]:
    rng = random.Random(seed if seed is not None else random.randint(0, 2**32))
    maze: list[list[str]] = [['W'] * cols for _ in range(rows)]
    steps: list[tuple[int, int]] = []

    start = _connect(entry, rows, cols)
    stack = [start]
    maze[start[0]][start[1]] = ' '
    steps.append(start)

    while stack:
        r, c = stack[-1]
        nbrs = []
        for dr, dc in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            nr, nc = r + dr, c + dc
            if (1 <= nr < rows - 1 and 1 <= nc < cols - 1
                    and maze[nr][nc] == 'W'
                    and (nr, nc) not in logo_cells):
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

    for cell in (entry, _border_neighbor(entry, rows, cols),
                 exit_,  _border_neighbor(exit_,  rows, cols)):
        r, c = cell
        if maze[r][c] == 'W':
            steps.append(cell)
        maze[r][c] = ' '

    if not perfect:
        for _ in range(max(1, (rows * cols) // 30)):
            r = rng.randint(1, rows - 2)
            c = rng.randint(1, cols - 2)
            if maze[r][c] == 'W' and (r, c) not in logo_cells:
                maze[r][c] = ' '
                steps.append((r, c))

    for r, c in logo_cells:
        maze[r][c] = 'W'

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
    q: deque[tuple[int, int]] = deque([entry])
    parent: dict[tuple[int, int], Optional[tuple[int, int]]] = {entry: None}

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
    rows = len(maze)
    cols = len(maze[0])

    def is_wall(r: int, c: int, dr: int, dc: int) -> bool:
        nr, nc = r + dr, c + dc
        if nr < 0 or nr >= rows or nc < 0 or nc >= cols:
            return True
        return maze[nr][nc] == 'W'

    lines: list[str] = []

    for r in range(rows):
        row_str = ""
        for c in range(cols):
            north = 1 if is_wall(r, c, -1,  0) else 0
            east  = 1 if is_wall(r, c,  0,  1) else 0
            south = 1 if is_wall(r, c,  1,  0) else 0
            west  = 1 if is_wall(r, c,  0, -1) else 0
            val = north | (east << 1) | (south << 2) | (west << 3)
            row_str += format(val, 'X')
        lines.append(row_str)

    lines.append("")

    lines.append(f"{entry[1]},{entry[0]}")
    lines.append(f"{exit_[1]},{exit_[0]}")

    direction_map: dict[tuple[int, int], str] = {
        (-1,  0): 'N',
        ( 1,  0): 'S',
        ( 0, -1): 'W',
        ( 0,  1): 'E',
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
        print(f"\033[91m[ERROR] Cannot write to '{output_file}': {e}\033[0m")
