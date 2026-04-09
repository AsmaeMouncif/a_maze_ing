*This project has been created as part of the 42 curriculum by \<moboulir>[, \<asmounci\>].*

---

# A-Maze-ing 🌀

## Description

A-Maze-ing is a terminal-based maze generator and solver written in Python. The program reads a configuration file, generates a random maze using the **Recursive Backtracker** algorithm, finds the shortest path from entry to exit using BFS, and saves the result to an output file. It also provides a fully interactive terminal visual with real-time animations, 7 color themes, and an embedded **42** logo pattern made of wall cells.

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
- No external libraries required for the main program

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

Cells are stored row by row, one row per line. After an empty line, the file contains 3 more lines: entry coordinates, exit coordinates, and the shortest path as a sequence of `N`, `S`, `E`, `W` letters.

---

## Maze Generation Algorithm

**Algorithm chosen: Recursive Backtracker (Depth-First Search)**

The algorithm works as follows:

1. Start from a cell connected to the entry point.
2. Randomly choose an unvisited neighbor, carve a passage to it, and push it onto a stack.
3. If no unvisited neighbors exist, backtrack (pop the stack) until one is found.
4. Repeat until the stack is empty — every cell has been visited.

**Why this algorithm?**

- It produces mazes with a single long winding path (perfect mazes), which are visually interesting and challenging to solve.
- It maps naturally to an animation: each carve step can be shown in real time, making the generation process engaging to watch.
- It is simple to implement correctly, easy to control with a seed for reproducibility, and efficient enough for the maze sizes supported (up to 99×99).
- The deep, river-like corridors it creates contrast clearly with the solid **42** logo wall pattern at the center.

In imperfect mode (`PERFECT=False`), extra walls are randomly removed — but only at valid passage positions (where exactly one of row/column is even) to avoid creating visual artefacts.

---