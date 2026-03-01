import random
from collections import deque
from typing import Optional

NORTH: int = 0b0001
EAST: int  = 0b0010
SOUTH: int = 0b0100
WEST: int  = 0b1000

DIR_FLAGS: dict[tuple[int, int], int] = {
    (-1,  0): NORTH,
    ( 0,  1): EAST,
    ( 1,  0): SOUTH,
    ( 0, -1): WEST,
}

OPPOSITE: dict[int, int] = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST:  WEST,
    WEST:  EAST,
}

PATTERN_42: list[tuple[int, int]] = [
    (0, 0), (1, 0), (2, 0), (2, 1), (2, 2),
    (0, 2), (1, 2),
    (3, 2), (4, 2),
    (0, 4), (0, 5), (0, 6),
    (1, 6),
    (2, 4), (2, 5), (2, 6),
    (3, 4),
    (4, 4), (4, 5), (4, 6),
]

PATTERN_ROWS: int = 5
PATTERN_COLS: int = 7


class MazeGenerator:
    def __init__(
        self,
        rows: int = 21,
        cols: int = 21,
        entry: tuple[int, int] = (1, 0),
        exit_: tuple[int, int] = (19, 20),
        perfect: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        self._rows: int = rows if rows % 2 == 1 else rows + 1
        self._cols: int = cols if cols % 2 == 1 else cols + 1
        self._entry: tuple[int, int] = entry
        self._exit: tuple[int, int] = exit_
        self._perfect: bool = perfect
        self._seed: Optional[int] = seed

        self._rng: random.Random = random.Random(seed)

        self._walls: list[list[int]] = [
            [0] * self._cols for _ in range(self._rows)
        ]
        self._grid: list[list[str]] = []
        self._solution: list[tuple[int, int]] = []
        self._carve_steps: list[tuple[int, int]] = []

        self._generate()

    def get_grid(self) -> list[list[str]]:
        return [row[:] for row in self._grid]

    def get_solution(self) -> list[tuple[int, int]]:
        return list(self._solution)

    def get_solution_string(self) -> str:
        if len(self._solution) < 2:
            return ""
        moves: list[str] = []
        dir_map: dict[tuple[int, int], str] = {
            (-1, 0): "N", (1, 0): "S", (0, -1): "W", (0, 1): "E"
        }
        for i in range(1, len(self._solution)):
            r0, c0 = self._solution[i - 1]
            r1, c1 = self._solution[i]
            key = (r1 - r0, c1 - c0)
            moves.append(dir_map.get(key, "?"))
        return "".join(moves)

    def get_carve_steps(self) -> list[tuple[int, int]]:
        return list(self._carve_steps)

    def get_wall_grid(self) -> list[list[int]]:
        return [row[:] for row in self._walls]

    def get_entry(self) -> tuple[int, int]:
        return self._entry

    def get_exit(self) -> tuple[int, int]:
        return self._exit

    def _generate(self) -> None:
        rows, cols = self._rows, self._cols

        grid: list[list[str]] = [['W'] * cols for _ in range(rows)]

        self._carve_steps = []
        grid[1][1] = ' '
        self._carve_steps.append((1, 1))
        self._carve(grid, 1, 1)

        self._place_42(grid)

        if not self._perfect:
            self._add_loops(grid)

        er, ec = self._entry
        grid[er][ec] = 'E'
        self._carve_steps.append((er, ec))
        self._open_inward(grid, er, ec, record_steps=True)

        xr, xc = self._exit
        grid[xr][xc] = 'X'
        self._carve_steps.append((xr, xc))
        self._open_inward(grid, xr, xc, record_steps=True)

        self._grid = grid

        self._compute_wall_bits()

        self._solution = self._bfs_solve()

    def _carve(self, grid: list[list[str]], r: int, c: int) -> None:
        rows, cols = self._rows, self._cols
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        self._rng.shuffle(directions)

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and grid[nr][nc] == 'W':
                wr, wc = r + dr // 2, c + dc // 2
                grid[wr][wc] = ' '
                grid[nr][nc] = ' '
                self._carve_steps.append((wr, wc))
                self._carve_steps.append((nr, nc))
                self._carve(grid, nr, nc)

    def _open_inward(self, grid: list[list[str]], r: int, c: int, record_steps: bool = False) -> None:
        rows, cols = self._rows, self._cols
        on_top = r == 0
        on_bot = r == rows - 1
        on_lft = c == 0
        on_rgt = c == cols - 1
        is_corner = (on_top or on_bot) and (on_lft or on_rgt)

        if is_corner:
            dr = 1 if on_top else -1
            dc = 1 if on_lft else -1
            if 0 <= r + dr < rows:
                if grid[r + dr][c] == 'W':
                    grid[r + dr][c] = ' '
                    if record_steps:
                        self._carve_steps.append((r + dr, c))
            if 0 <= c + dc < cols:
                if grid[r][c + dc] == 'W':
                    grid[r][c + dc] = ' '
                    if record_steps:
                        self._carve_steps.append((r, c + dc))
            if 0 <= r + dr < rows and 0 <= c + dc < cols:
                if grid[r + dr][c + dc] == 'W':
                    grid[r + dr][c + dc] = ' '
                    if record_steps:
                        self._carve_steps.append((r + dr, c + dc))
        else:
            if on_top:
                dr, dc = 1, 0
            elif on_bot:
                dr, dc = -1, 0
            elif on_lft:
                dr, dc = 0, 1
            else:
                dr, dc = 0, -1

            nr, nc = r + dr, c + dc
            while 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] in (' ', 'E', 'X'):
                    break
                grid[nr][nc] = ' '
                if record_steps:
                    self._carve_steps.append((nr, nc))
                nr += dr
                nc += dc

    def _border_neighbors(self, r: int, c: int) -> list[tuple[int, int]]:
        rows, cols = self._rows, self._cols
        candidates: list[tuple[int, int]] = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1:
                candidates.append((nr, nc))
        return candidates

    def _border_interior(self, r: int, c: int) -> tuple[int, int]:
        rows, cols = self._rows, self._cols
        if r == 0 and 0 < c < cols - 1:
            return (1, c)
        if r == rows - 1 and 0 < c < cols - 1:
            return (rows - 2, c)
        if c == 0 and 0 < r < rows - 1:
            return (r, 1)
        if c == cols - 1 and 0 < r < rows - 1:
            return (r, cols - 2)
        if r == 0 and c == 0:
            return (1, 1)
        if r == 0 and c == cols - 1:
            return (1, cols - 2)
        if r == rows - 1 and c == 0:
            return (rows - 2, 1)
        if r == rows - 1 and c == cols - 1:
            return (rows - 2, cols - 2)
        return (r, c)

    def _place_42(self, grid: list[list[str]]) -> None:
        rows, cols = self._rows, self._cols
        if rows < PATTERN_ROWS + 4 or cols < PATTERN_COLS + 4:
            print("[ERROR] Maze too small to display the '42' pattern.")
            return

        start_r = (rows - PATTERN_ROWS) // 2
        start_c = (cols - PATTERN_COLS) // 2

        for dr, dc in PATTERN_42:
            pr, pc = start_r + dr, start_c + dc
            if 0 < pr < rows - 1 and 0 < pc < cols - 1:
                if grid[pr][pc] == 'W':
                    grid[pr][pc] = '*'

    def _add_loops(self, grid: list[list[str]]) -> None:
        rows, cols = self._rows, self._cols
        candidates: list[tuple[int, int]] = []
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if grid[r][c] == 'W':
                    if (r % 2 == 0 and grid[r - 1][c] == ' ' and grid[r + 1][c] == ' '):
                        candidates.append((r, c))
                    elif (c % 2 == 0 and grid[r][c - 1] == ' ' and grid[r][c + 1] == ' '):
                        candidates.append((r, c))

        remove_count = max(1, len(candidates) // 7)
        chosen = self._rng.sample(candidates, min(remove_count, len(candidates)))
        for r, c in chosen:
            grid[r][c] = ' '

    def _compute_wall_bits(self) -> None:
        rows, cols = self._rows, self._cols
        grid = self._grid

        passable = {' ', 'E', 'X'}

        for r in range(rows):
            for c in range(cols):
                bits = 0
                for (dr, dc), flag in DIR_FLAGS.items():
                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < rows and 0 <= nc < cols):
                        if grid[r][c] not in ('E', 'X'):
                            bits |= flag
                    elif grid[nr][nc] not in passable:
                        bits |= flag
                self._walls[r][c] = bits

    def _bfs_solve(self) -> list[tuple[int, int]]:
        rows, cols = self._rows, self._cols
        grid = self._grid
        passable = {' ', 'E', 'X'}

        start = end = None
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 'E':
                    start = (r, c)
                elif grid[r][c] == 'X':
                    end = (r, c)

        if start is None or end is None:
            print("[ERROR] Could not find Entry or Exit in maze.")
            return []

        queue: deque[list[tuple[int, int]]] = deque([[start]])
        visited: set[tuple[int, int]] = {start}

        while queue:
            path = queue.popleft()
            r, c = path[-1]
            if (r, c) == end:
                return path
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < rows and 0 <= nc < cols
                        and (nr, nc) not in visited
                        and grid[nr][nc] in passable):
                    visited.add((nr, nc))
                    queue.append(path + [(nr, nc)])

        print("[ERROR] No path found between entry and exit.")
        return []