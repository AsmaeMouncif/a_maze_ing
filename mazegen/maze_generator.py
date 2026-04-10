"""
Reusable maze generator module.

This module provides the MazeGenerator class, which can be imported
and used independently in any Python project.

Basic usage example::

    from mazegen import MazeGenerator

    gen = MazeGenerator(width=21, height=15, seed=42)
    gen.generate()

    # Access the maze grid
    maze = gen.maze        # 2D list of str ('W', ' ', 'E', 'X')

    # Solve from entry to exit
    path = gen.solve()     # list of (row, col) tuples

    # Export to hex file
    gen.save("maze.txt")

    # Access solution as directions
    directions = gen.path_directions()  # e.g. "SSEENNW..."
"""

import random
from collections import deque
from typing import Optional


def _make_odd(n: int, upper: int) -> int:
    """Clamp n inside [1, upper-2] and ensure it is odd.

    Args:
        n: Value to clamp and adjust.
        upper: Exclusive upper bound.

    Returns:
        An odd integer clamped within [1, upper-2].
    """
    v = max(1, min(n, upper - 2))
    return v if v % 2 == 1 else (v - 1 if v > 1 else v + 1)


def _border_neighbor(
    pos: tuple[int, int], rows: int, cols: int
) -> tuple[int, int]:
    """Return the cell one step inward from a border cell.

    Args:
        pos: (row, col) of the border cell.
        rows: Total number of rows.
        cols: Total number of columns.

    Returns:
        (row, col) of the adjacent interior cell.
    """
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
    """Return the nearest odd-indexed interior cell connected to pos.

    Args:
        pos: (row, col) border position.
        rows: Total number of rows.
        cols: Total number of columns.

    Returns:
        (row, col) of the nearest odd-indexed interior cell.
    """
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

    Args:
        maze: Current 2-D grid ('W' = wall).
        rows: Number of rows.
        cols: Number of columns.
        tr: Row of the candidate cell.
        tc: Column of the candidate cell.

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


class MazeGenerator:
    """Generate, solve, and export mazes using the Recursive Backtracker.

    The maze is built on an odd-indexed grid so every carved cell is
    separated by exactly one wall cell, guaranteeing a perfect maze by
    construction. In imperfect mode, extra passages are added safely
    without creating 2x2 open areas.

    Attributes:
        width (int): Requested maze width (number of cells).
        height (int): Requested maze height (number of cells).
        entry (tuple[int, int]): Entry cell as (row, col).
        exit_ (tuple[int, int]): Exit cell as (row, col).
        perfect (bool): Whether the maze is perfect (single path).
        seed (Optional[int]): Random seed used for generation.
        maze (list[list[str]]): 2D grid after generate() is called.
        carve_steps (list[tuple[int, int]]): Ordered carved cells.

    Example::

        gen = MazeGenerator(width=21, height=15, seed=42)
        gen.generate()
        path = gen.solve()
        gen.save("output.txt")
    """

    def __init__(
        self,
        width: int = 21,
        height: int = 15,
        entry: tuple[int, int] = (0, 0),
        exit_: Optional[tuple[int, int]] = None,
        perfect: bool = True,
        seed: Optional[int] = None,
        logo_cells: Optional[set[tuple[int, int]]] = None,
    ) -> None:
        """Initialise the MazeGenerator with the given parameters.

        Args:
            width: Maze width in cells (will be rounded up to odd).
                Must be >= 5. Defaults to 21.
            height: Maze height in cells (will be rounded up to odd).
                Must be >= 5. Defaults to 15.
            entry: Entry cell as (row, col). Must be on the border.
                Defaults to (0, 0).
            exit_: Exit cell as (row, col). Must be on the border and
                different from entry. Defaults to bottom-right corner.
            perfect: If True, generates a perfect maze (one unique path
                between any two cells). If False, adds extra passages.
                Defaults to True.
            seed: Random seed for reproducibility. None means random.
                Defaults to None.
            logo_cells: Set of (row, col) positions to keep as walls
                (used for the '42' logo pattern). Defaults to empty set.

        Raises:
            ValueError: If width or height is less than 5, or if entry
                and exit_ are the same cell.
        """
        if width < 5 or height < 5:
            raise ValueError(
                f"Width and height must be >= 5, got {width}x{height}."
            )

        # Round up to odd to fit the grid algorithm
        self.cols: int = width if width % 2 == 1 else width + 1
        self.rows: int = height if height % 2 == 1 else height + 1
        self.width: int = width
        self.height: int = height

        self.entry: tuple[int, int] = entry
        self.exit_: tuple[int, int] = (
            exit_ if exit_ is not None else (self.rows - 1, self.cols - 1)
        )

        if self.entry == self.exit_:
            raise ValueError("Entry and exit must be different cells.")

        self.perfect: bool = perfect
        self.seed: Optional[int] = seed
        self.logo_cells: set[tuple[int, int]] = (
            logo_cells if logo_cells is not None else set()
        )

        # These are set after generate() is called
        self.maze: list[list[str]] = []
        self.carve_steps: list[tuple[int, int]] = []
        self._solution: list[tuple[int, int]] = []

    def generate(self) -> "MazeGenerator":
        """Run the maze generation algorithm.

        Uses the Recursive Backtracker (DFS) on odd-indexed cells.
        Populates self.maze and self.carve_steps.

        Returns:
            self, so you can chain: gen.generate().solve()
        """
        rows = self.rows
        cols = self.cols
        logo_cells = self.logo_cells
        entry = self.entry
        exit_ = self.exit_

        rng = random.Random(
            self.seed if self.seed is not None
            else random.randint(0, 2 ** 32)
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
        if not self.perfect:
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

        self.maze = maze
        self.carve_steps = steps
        self._solution = []  # reset any previous solution
        return self

    def solve(self) -> list[tuple[int, int]]:
        """Find the shortest path from entry to exit using BFS.

        Must be called after generate().

        Returns:
            Ordered list of (row, col) positions from entry to exit,
            inclusive. Returns an empty list if no path exists.

        Raises:
            RuntimeError: If generate() has not been called yet.
        """
        if not self.maze:
            raise RuntimeError(
                "Call generate() before solve()."
            )

        maze = self.maze
        entry = self.entry
        exit_ = self.exit_

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
            self._solution = []
            return []

        path: list[tuple[int, int]] = []
        cur: Optional[tuple[int, int]] = exit_
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        self._solution = path
        return path

    def path_directions(self) -> str:
        """Convert the solution path to a direction string (N/S/E/W).

        Must be called after solve().

        Returns:
            A string of direction letters, e.g. 'SSEENNW'.
            Returns empty string if no solution exists.
        """
        path = self._solution
        direction_map: dict[tuple[int, int], str] = {
            (-1, 0): 'N',
            (1, 0): 'S',
            (0, -1): 'W',
            (0, 1): 'E',
        }
        result = ""
        for i in range(1, len(path)):
            dr = path[i][0] - path[i - 1][0]
            dc = path[i][1] - path[i - 1][1]
            result += direction_map.get((dr, dc), '?')
        return result

    def save(self, output_file: str) -> None:
        """Encode the maze as hex digits and write it to a file.

        Each cell is one uppercase hex digit encoding which walls are
        closed (bit=1) or open (bit=0):

        * bit 0 (LSB) → North
        * bit 1       → East
        * bit 2       → South
        * bit 3       → West

        After the grid rows, an empty line precedes three metadata lines:
        entry coordinates, exit coordinates, and the path as N/E/S/W.

        Args:
            output_file: Destination file path.

        Raises:
            RuntimeError: If generate() has not been called yet.
        """
        if not self.maze:
            raise RuntimeError(
                "Call generate() before save()."
            )

        if not self._solution:
            self.solve()

        maze = self.maze
        rows = len(maze)
        cols = len(maze[0])
        entry = self.entry
        exit_ = self.exit_

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
        lines.append(self.path_directions())

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")
        except OSError as e:
            print(
                f"\033[91m[ERROR] Cannot write to '{output_file}': {e}\033[0m"
            )
