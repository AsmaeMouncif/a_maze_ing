# mazegen — Reusable Maze Generator

A standalone Python package for generating, solving, and exporting mazes
using the **Recursive Backtracker** (DFS) algorithm.

---

## Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

Or from source:

```bash
pip install build
python -m build
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

---

## Quick Start

```python
from mazegen import MazeGenerator

# Basic usage — 21 wide, 15 tall, perfect maze, reproducible seed
gen = MazeGenerator(width=21, height=15, seed=42)
gen.generate()

# Solve from entry to exit
path = gen.solve()
print(f"Solution length: {len(path)} cells")

# Get directions as a string (N, S, E, W)
print(gen.path_directions())   # e.g. "SSSEEENNW..."

# Save to a hex-encoded file
gen.save("maze.txt")
```

---

## Custom Parameters

```python
gen = MazeGenerator(
    width=31,                  # maze width  (>= 5, rounded up to odd)
    height=21,                 # maze height (>= 5, rounded up to odd)
    entry=(0, 0),              # entry as (row, col), must be on border
    exit_=(20, 30),            # exit  as (row, col), must be on border
    perfect=True,              # True = one path; False = extra passages
    seed=1234,                 # fixed seed for reproducibility
    logo_cells=set(),          # optional set of (row,col) kept as walls
)
gen.generate()
```

---

## Accessing the Generated Structure

| Attribute / Method | Type | Description |
|---|---|---|
| `gen.maze` | `list[list[str]]` | 2D grid: `'W'`=wall, `' '`=open, `'E'`=entry, `'X'`=exit |
| `gen.carve_steps` | `list[tuple[int,int]]` | Ordered list of cells carved during generation |
| `gen.rows` / `gen.cols` | `int` | Actual grid dimensions (rounded up to odd) |
| `gen.solve()` | `list[tuple[int,int]]` | Shortest path from entry to exit (BFS) |
| `gen.path_directions()` | `str` | Path as N/S/E/W string |
| `gen.save(path)` | `None` | Save hex-encoded maze file |

---

## Full Example

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=15, height=11, seed=99, perfect=False)
gen.generate()
path = gen.solve()

# Print the maze in ASCII
for r, row in enumerate(gen.maze):
    line = ""
    for c, cell in enumerate(row):
        if (r, c) in set(path):
            line += "· "
        elif cell == 'W':
            line += "██"
        elif cell == 'E':
            line += "IN"
        elif cell == 'X':
            line += "OUT"
        else:
            line += "  "
    print(line)

print(f"\nPath: {gen.path_directions()}")
gen.save("my_maze.txt")
```