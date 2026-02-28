"""
maze_generator.py — Reusable maze generation module for A-Maze-ing.

This module provides the MazeGenerator class which generates mazes
using the Recursive Backtracker (DFS) algorithm.

Usage example:
    from maze_generator import MazeGenerator

    mg = MazeGenerator(rows=21, cols=21, entry=(0, 1), exit_=(20, 19),
                       perfect=True, seed=42)
    grid = mg.get_grid()       # list[list[str]]
    solution = mg.get_solution()  # list[tuple[int, int]]
    path_str = mg.get_solution_string()  # e.g. "SSEENNW..."

Algorithm: Recursive Backtracker (DFS)
    - Starts from an interior cell and carves passages using DFS.
    - Produces a perfect maze (unique path between any two cells).
    - When PERFECT=False, extra walls are removed randomly to create loops.

Grid legend:
    'W'  — wall
    ' '  — open passage
    'E'  — entry cell
    'X'  — exit cell
"""

import random
from collections import deque
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
#  Wall encoding constants (for hex output)
# ─────────────────────────────────────────────────────────────────────────────

NORTH: int = 0b0001  # bit 0
EAST: int  = 0b0010  # bit 1
SOUTH: int = 0b0100  # bit 2
WEST: int  = 0b1000  # bit 3

# Map direction vectors to bit flags
DIR_FLAGS: dict[tuple[int, int], int] = {
    (-1,  0): NORTH,
    ( 0,  1): EAST,
    ( 1,  0): SOUTH,
    ( 0, -1): WEST,
}

# Opposite direction
OPPOSITE: dict[int, int] = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST:  WEST,
    WEST:  EAST,
}

# ─────────────────────────────────────────────────────────────────────────────
#  "42" pattern — defined as relative (row, col) offsets of CLOSED cells
#  The pattern fits in a 5-row × 9-col bounding box.
#  Both digits are drawn with fully-closed cells ('W').
# ─────────────────────────────────────────────────────────────────────────────

PATTERN_42: list[tuple[int, int]] = [
    # digit "4"
    (0, 0), (1, 0), (2, 0), (2, 1), (2, 2),
    (0, 2), (1, 2),
    (3, 2), (4, 2),
    # digit "2"
    (0, 4), (0, 5), (0, 6),
    (1, 6),
    (2, 4), (2, 5), (2, 6),
    (3, 4),
    (4, 4), (4, 5), (4, 6),
]

PATTERN_ROWS: int = 5
PATTERN_COLS: int = 7  # 0..6


class MazeGenerator:
    """
    Generate a maze using the Recursive Backtracker (DFS) algorithm.

    The internal grid uses odd-indexed cells as passable rooms and
    even-indexed cells as potential walls between rooms.

    Args:
        rows:    Height of the maze in cells (will be made odd if even).
        cols:    Width  of the maze in cells (will be made odd if even).
        entry:   (row, col) on the border — entry cell.
        exit_:   (row, col) on the border — exit cell.
        perfect: If True, generate a perfect maze (no loops).
                 If False, add extra openings for multiple paths.
        seed:    Integer seed for reproducibility. None = random.

    Example:
        mg = MazeGenerator(rows=15, cols=20, entry=(0, 1),
                           exit_=(14, 19), perfect=True, seed=42)
        grid     = mg.get_grid()
        solution = mg.get_solution()
    """

    def __init__(
        self,
        rows: int = 21,
        cols: int = 21,
        entry: tuple[int, int] = (1, 0),
        exit_: tuple[int, int] = (19, 20),
        perfect: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        """Initialise and generate the maze immediately."""
        self._rows: int = rows if rows % 2 == 1 else rows + 1
        self._cols: int = cols if cols % 2 == 1 else cols + 1
        self._entry: tuple[int, int] = entry
        self._exit: tuple[int, int] = exit_
        self._perfect: bool = perfect
        self._seed: Optional[int] = seed

        self._rng: random.Random = random.Random(seed)

        # wall-bit grid: walls[r][c] = bitmask of CLOSED walls
        self._walls: list[list[int]] = [
            [0] * self._cols for _ in range(self._rows)
        ]
        # passage grid for display: 'W', ' ', 'E', 'X'
        self._grid: list[list[str]] = []
        self._solution: list[tuple[int, int]] = []

        self._generate()

    # ─────────────────────────────────────────────
    #  Public API
    # ─────────────────────────────────────────────

    def get_grid(self) -> list[list[str]]:
        """
        Return the maze as a 2D character grid.

        Returns:
            list[list[str]]: Grid where each cell is one of:
                'W' — wall / closed cell
                ' ' — open passage
                'E' — entry
                'X' — exit
        """
        return [row[:] for row in self._grid]

    def get_solution(self) -> list[tuple[int, int]]:
        """
        Return the shortest path from entry to exit.

        Returns:
            list[tuple[int, int]]: Ordered list of (row, col) from entry to exit.
                Empty list if no path exists.
        """
        return list(self._solution)

    def get_solution_string(self) -> str:
        """
        Return the solution as a string of direction letters.

        Returns:
            str: Sequence of 'N', 'E', 'S', 'W' from entry to exit.
        """
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

    def get_wall_grid(self) -> list[list[int]]:
        """
        Return a 2D grid of wall bitmasks (hex output format).

        Each integer uses bits: 0=North, 1=East, 2=South, 3=West.
        A set bit means the wall in that direction is CLOSED.

        Returns:
            list[list[int]]: rows × cols grid of integers 0-15.
        """
        return [row[:] for row in self._walls]

    def get_entry(self) -> tuple[int, int]:
        """Return the entry (row, col)."""
        return self._entry

    def get_exit(self) -> tuple[int, int]:
        """Return the exit (row, col)."""
        return self._exit

    # ─────────────────────────────────────────────
    #  Internal generation
    # ─────────────────────────────────────────────

    def _generate(self) -> None:
        """Run the full maze generation pipeline."""
        rows, cols = self._rows, self._cols

        # Step 1: start with all walls closed
        grid: list[list[str]] = [['W'] * cols for _ in range(rows)]

        # Step 2: carve passages with recursive backtracker
        grid[1][1] = ' '
        self._carve(grid, 1, 1)

        # Step 3: place the "42" pattern (fully closed cells)
        self._place_42(grid)

        # Step 4: if not perfect, remove extra walls to add loops
        if not self._perfect:
            self._add_loops(grid)

        # Step 5: place entry and exit and carve a passage inward
        er, ec = self._entry
        grid[er][ec] = 'E'
        self._open_inward(grid, er, ec)

        xr, xc = self._exit
        grid[xr][xc] = 'X'
        self._open_inward(grid, xr, xc)

        self._grid = grid

        # Step 6: compute wall bitmasks
        self._compute_wall_bits()

        # Step 7: solve
        self._solution = self._bfs_solve()

    def _carve(self, grid: list[list[str]], r: int, c: int) -> None:
        """
        Recursively carve passages from cell (r, c) using DFS.

        Args:
            grid: The mutable maze grid.
            r:    Current row (odd index = room cell).
            c:    Current column.
        """
        rows, cols = self._rows, self._cols
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        self._rng.shuffle(directions)

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and grid[nr][nc] == 'W':
                grid[r + dr // 2][c + dc // 2] = ' '
                grid[nr][nc] = ' '
                self._carve(grid, nr, nc)

    def _open_inward(self, grid: list[list[str]], r: int, c: int) -> None:
        """
        Carve an open passage from border cell (r,c) to the nearest interior room.

        For edge cells: walks one step inward.
        For corner cells: walks along one border axis until reaching an
        interior cell, then opens the connecting wall.

        Args:
            grid: Mutable maze grid.
            r:    Row of the border/entry/exit cell.
            c:    Column of the border/entry/exit cell.
        """
        rows, cols = self._rows, self._cols
        on_top = r == 0
        on_bot = r == rows - 1
        on_lft = c == 0
        on_rgt = c == cols - 1
        is_corner = (on_top or on_bot) and (on_lft or on_rgt)

        if is_corner:
            # For a corner, we need to open the cell diagonally inward.
            # Walk along the row border until we can step into the interior,
            # then walk inward to connect.
            # Simpler: just open the cell (r±1, c) and (r, c±1) if they exist
            # and are walls, then open the diagonal (r±1, c±1).
            dr = 1 if on_top else -1
            dc = 1 if on_lft else -1
            # Open the two adjacent border cells
            if 0 <= r + dr < rows:
                if grid[r + dr][c] == 'W':
                    grid[r + dr][c] = ' '
            if 0 <= c + dc < cols:
                if grid[r][c + dc] == 'W':
                    grid[r][c + dc] = ' '
            # Open the interior diagonal cell to ensure connectivity
            if 0 <= r + dr < rows and 0 <= c + dc < cols:
                if grid[r + dr][c + dc] == 'W':
                    grid[r + dr][c + dc] = ' '
        else:
            # Regular edge cell: determine single inward direction
            if on_top:
                dr, dc = 1, 0
            elif on_bot:
                dr, dc = -1, 0
            elif on_lft:
                dr, dc = 0, 1
            else:
                dr, dc = 0, -1

            # Walk inward until we reach an already-open interior cell
            nr, nc = r + dr, c + dc
            while 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] in (' ', 'E', 'X'):
                    break
                grid[nr][nc] = ' '
                nr += dr
                nc += dc

    def _border_neighbors(self, r: int, c: int) -> list[tuple[int, int]]:
        """
        Return orthogonal interior neighbours of a border cell, inward first.

        Args:
            r: Row of the border cell.
            c: Column of the border cell.

        Returns:
            List of (row, col) candidates ordered by how far inward they go.
        """
        rows, cols = self._rows, self._cols
        candidates: list[tuple[int, int]] = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1:
                candidates.append((nr, nc))
        return candidates

    def _border_interior(self, r: int, c: int) -> tuple[int, int]:
        """
        Return the first interior cell adjacent to border cell (r, c).

        For corner cells, prefer the interior cell that leads inward.

        Args:
            r: Row of the border cell.
            c: Column of the border cell.

        Returns:
            (row, col) of the adjacent interior cell.
        """
        rows, cols = self._rows, self._cols
        # Priority: top/bottom over left/right
        if r == 0 and 0 < c < cols - 1:
            return (1, c)
        if r == rows - 1 and 0 < c < cols - 1:
            return (rows - 2, c)
        if c == 0 and 0 < r < rows - 1:
            return (r, 1)
        if c == cols - 1 and 0 < r < rows - 1:
            return (r, cols - 2)
        # Corner cases: pick the diagonal interior cell
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
        """
        Embed the '42' pattern into the maze as fully-closed wall cells.

        Only sets cells that are already walls — never overwrites open passages,
        ensuring the maze remains fully connected.
        Prints an error if the maze is too small to fit the pattern.

        Args:
            grid: The mutable maze grid (modified in place).
        """
        rows, cols = self._rows, self._cols
        # Need room for pattern + 1-cell margin on each side
        if rows < PATTERN_ROWS + 4 or cols < PATTERN_COLS + 4:
            print("[ERROR] Maze too small to display the '42' pattern.")
            return

        # Centre the pattern (avoid the outer border row/col)
        start_r = (rows - PATTERN_ROWS) // 2
        start_c = (cols - PATTERN_COLS) // 2

        for dr, dc in PATTERN_42:
            pr, pc = start_r + dr, start_c + dc
            if 0 < pr < rows - 1 and 0 < pc < cols - 1:
                # Only reinforce walls — never close open passages
                if grid[pr][pc] == 'W':
                    grid[pr][pc] = 'W'  # already a wall, keep it
                # If it's an open cell, we skip it to preserve connectivity

    def _add_loops(self, grid: list[list[str]]) -> None:
        """
        Remove a fraction of interior walls to create multiple paths.

        Args:
            grid: The mutable maze grid (modified in place).
        """
        rows, cols = self._rows, self._cols
        # Collect all removable interior wall cells (even-indexed = wall between rooms)
        candidates: list[tuple[int, int]] = []
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if grid[r][c] == 'W':
                    # It's a wall between two rooms if neighbours are open
                    if (r % 2 == 0 and grid[r - 1][c] == ' ' and grid[r + 1][c] == ' '):
                        candidates.append((r, c))
                    elif (c % 2 == 0 and grid[r][c - 1] == ' ' and grid[r][c + 1] == ' '):
                        candidates.append((r, c))

        # Remove ~15 % of candidate walls
        remove_count = max(1, len(candidates) // 7)
        chosen = self._rng.sample(candidates, min(remove_count, len(candidates)))
        for r, c in chosen:
            grid[r][c] = ' '

    def _compute_wall_bits(self) -> None:
        """
        Build the self._walls bitmask grid from self._grid.

        Bit 0 (NORTH) is set if there is a wall to the north, etc.
        Border cells always have their outer wall closed.
        Entry/Exit cells have their outer border wall open.
        """
        rows, cols = self._rows, self._cols
        grid = self._grid

        passable = {' ', 'E', 'X'}

        for r in range(rows):
            for c in range(cols):
                bits = 0
                for (dr, dc), flag in DIR_FLAGS.items():
                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < rows and 0 <= nc < cols):
                        # Outside maze → wall closed (unless it's entry/exit opening)
                        if grid[r][c] not in ('E', 'X'):
                            bits |= flag
                    elif grid[nr][nc] not in passable:
                        bits |= flag
                self._walls[r][c] = bits

    def _bfs_solve(self) -> list[tuple[int, int]]:
        """
        Find the shortest path from entry to exit using BFS.

        Returns:
            list[tuple[int, int]]: Ordered path from entry to exit,
                or empty list if unreachable.
        """
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