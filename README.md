*This project has been created as part of the 42 curriculum by \<moboulir>, \<asmounci>.*

---

# A-Maze-ing 🌀

## Description

A-Maze-ing is a terminal-based maze generator and solver written in Python. The program reads a configuration file, generates a random maze using the **Recursive Backtracker** algorithm, finds the shortest path from entry to exit using BFS, and saves the result to an output file.

It also provides a fully interactive terminal visual with real-time animations, 7 color themes, and an embedded **42** logo pattern made of wall cells.

Key features:
- Perfect maze mode (exactly one path between any two cells)
- Imperfect maze mode (extra passages create loops and multiple routes)
- Real-time animation of maze generation and path solving
- Interactive menu: re-generate, show/hide path, rotate colors, quit
- Output file in hexadecimal wall-bitmask format
- Reusable `mazegen` package installable via pip

---

## Instructions

### Requirements

- Python 3.10 or later
- Unix-like terminal with ANSI escape code support
- No external libraries required for the main program (`flake8` and `mypy` for linting only)

### Run

```bash
make run
# or directly:
python3 a_maze_ing.py config.txt
```

### Install dependencies

```bash
make install
```

### Lint

```bash
make lint
```

### Debug

```bash
make debug
```

### Clean

```bash
make clean
```

---

## Configuration File Format

The configuration file must contain one `KEY=VALUE` pair per line. Lines starting with `#` are comments and are ignored.

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `WIDTH` | int | Maze width in cells (5–99) | `WIDTH=20` |
| `HEIGHT` | int | Maze height in cells (5–99) | `HEIGHT=15` |
| `ENTRY` | col,row | Entry coordinates, must be on a border edge | `ENTRY=0,0` |
| `EXIT` | col,row | Exit coordinates, must be on a border edge | `EXIT=19,14` |
| `OUTPUT_FILE` | string | Path for the output maze file | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | True/False | Perfect maze (no loops) or imperfect | `PERFECT=True` |
| `SEED` | int | Fixed seed for reproducible generation (optional) | `SEED=42` |

Example `config.txt`:

```ini
# Maze dimensions
WIDTH=21
HEIGHT=15

# Entry on left border, exit on right border
ENTRY=0,0
EXIT=20,14

OUTPUT_FILE=maze.txt
PERFECT=True

# Optional seed for reproducibility
# SEED=42
```

---

## Output File Format

Each cell is encoded as one hexadecimal digit representing which of its 4 walls are closed (bit = 1) or open (bit = 0):

| Bit | Direction |
|-----|-----------|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 | West |

Cells are stored row by row, one row per line. After an empty line, the file contains 3 more lines: entry coordinates (col,row), exit coordinates (col,row), and the shortest path as a sequence of `N`, `S`, `E`, `W` letters.

---

## Maze Generation Algorithm

**Algorithm chosen: Recursive Backtracker (Depth-First Search)**

The algorithm works as follows:

1. Start from a cell connected to the entry point.
2. Randomly choose an unvisited neighbor, carve a passage to it, and push it onto a stack.
3. If no unvisited neighbors exist, backtrack (pop the stack) until one is found.
4. Repeat until the stack is empty — every cell has been visited.

**Why this algorithm?**

- It produces mazes with a single long winding path (perfect mazes), visually interesting and challenging to solve.
- It maps naturally to an animation: each carve step can be shown in real time.
- It is simple to implement correctly and easy to control with a seed for reproducibility.
- The deep, river-like corridors it creates contrast clearly with the solid **42** logo wall pattern.

In imperfect mode (`PERFECT=False`), extra walls are randomly removed — but only if the removal does not create a 2x2 open area.

---

## Reusable Module — `mazegen`

The maze generation logic is packaged as a standalone pip-installable module called `mazegen`. It exposes a single class `MazeGenerator` that can be imported and used in any Python project independently of this program.

### Install the package

```bash
# From the pre-built wheel at the repo root:
pip install mazegen-1.0.0-py3-none-any.whl
```

### Build from source

```bash
python3 -m venv build_env
source build_env/bin/activate
pip install build
python -m build
deactivate
```

### Test in a clean environment

```bash
python3 -m venv test_env
source test_env/bin/activate
pip install dist/mazegen-1.0.0-py3-none-any.whl
python3 -c "
from mazegen import MazeGenerator
gen = MazeGenerator(width=21, height=15, seed=42)
gen.generate()
path = gen.solve()
print('OK — path:', len(path), 'cells')
gen.save('test_output.txt')
"
deactivate
```

### Basic usage

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=21, height=15, seed=42)
gen.generate()

path = gen.solve()
print(f"Path: {len(path)} cells")
print(f"Directions: {gen.path_directions()}")

gen.save("maze.txt")
```

### Custom parameters

```python
gen = MazeGenerator(
    width=31,
    height=21,
    entry=(0, 0),       # (row, col), must be on the border
    exit_=(20, 30),     # (row, col), must be on the border
    perfect=True,
    seed=1234,
)
gen.generate()
path = gen.solve()
```

### Accessing the generated structure

| Attribute / Method | Type | Description |
|---|---|---|
| `gen.maze` | `list[list[str]]` | 2D grid: `'W'`=wall, `' '`=open, `'E'`=entry, `'X'`=exit |
| `gen.rows` / `gen.cols` | `int` | Actual grid dimensions (rounded up to odd) |
| `gen.carve_steps` | `list[tuple[int,int]]` | Ordered list of cells carved during generation |
| `gen.solve()` | `list[tuple[int,int]]` | Shortest path from entry to exit (BFS) |
| `gen.path_directions()` | `str` | Path as N/S/E/W string |
| `gen.save(path)` | `None` | Save hex-encoded maze to file |

---

## Team and Project Management

### Roles

| Member | Role |
|--------|------|
| `moboulir` | Maze generation algorithm, output file format, package architecture |
| `asmounci` | Visual display, animation, color system, terminal menu |

### Planning

**Anticipated planning:**
- Days 1–3: Setup, config parsing, generation algorithm
- Days 4–7: Output file format and BFS solver
- Days 8–13: Visual display, animation, terminal menu, arrow key interactions
- Days 14–17: Logo embedding, color themes, edge case handling
- Days 18–19: `mazegen` package, flake8 / mypy fixes
- Day 20: README, final tests, cleanup

**How it evolved:**
- The project took 20 days in total instead of the initially planned week.
- The logo embedding took significantly more time than expected — keeping it isolated without breaking maze connectivity was tricky.
- Animation and terminal rendering required a lot of debugging due to escape code quirks.
- The `mazegen` package refactoring into a class, writing the README, running flake8 and mypy to fix all warnings, and testing everything end-to-end all happened on the last day.

### What worked well
- The Recursive Backtracker produces great-looking mazes and maps naturally to the animation.
- The color rotation system and the 7 themes were satisfying to build.
- Working in parallel on generation and display saved a lot of time.

### What could be improved
- Supporting multiple generation algorithms (Prim's, Kruskal's) would make the maze variety richer and is a natural next step.
- The entry and exit positions are currently set in config — an interactive arrow-key selector directly in the terminal would improve the user experience.

### Tools used
- `mypy` and `flake8` for static analysis and style checking
- `pdb` for debugging
- `build` for packaging

---

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive Backtracker — Jamis Buck's blog](http://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [DFS and BFS algorithms — tutorials and visual explanations](https://www.youtube.com/results?search_query=dfs+bfs+algorithm+tutorial)
- [Python official documentation](https://docs.python.org/3/)
- [W3Schools Python reference](https://www.w3schools.com/python/)
- [Stack Overflow — debugging and syntax questions](https://stackoverflow.com)
- [ANSI 256 color codes — ColorPalette v0.1.10](https://share.google/C9GX8S8qLQFYkWiqP)
- [Python packaging guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [PEP 257 — Docstring conventions](https://peps.python.org/pep-0257/)

### AI Usage

During this project, we used AI as a learning and support tool to ask general questions when we were stuck — not to generate code. We always read and understood the answers before applying anything ourselves.
