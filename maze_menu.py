"""Main menu and runtime loop for the A-Maze-ing maze viewer."""

import sys
import signal
import random
from typing import Optional

from visual.config import load_config
from visual.colors import rotate_wall_color
from visual.logo import (
    logo_fits,
    get_logo_cells,
    _LOGO_H,
    _LOGO_W4,
    _LOGO_W2,
    _LOGO_GAP,
    _LOGO_S,
)
from visual.display import display_maze
from visual.terminal import clear_maze_display, flush_input
from visual.animation import animate_generation, animate_path
from core.maze_gen import generate_maze, find_path, write_maze_file


def display_menu() -> str:
    """Print the interactive menu and return the user's validated choice.

    Keeps prompting until the user enters a value in {'1', '2', '3', '4'}.
    Erases the invalid-input line before re-prompting to keep the display
    clean.

    Returns:
        A single character string: '1', '2', '3', or '4'.
    """
    print("=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show/Hide path from entry to exit")
    print("3. Rotate maze colors")
    print("4. Quit")
    choice: str = input("Choice? (1-4): ")
    while choice not in ("1", "2", "3", "4"):
        sys.stdout.write("\033[1A\033[2K")
        sys.stdout.flush()
        choice = input("Choice? (1-4): ")
    return choice


def run(config_path: str) -> None:
    """Load configuration and start the interactive maze display loop.

    Generates an initial maze, animates its construction and solution,
    then enters a menu loop allowing the user to re-generate, toggle
    the path, change colors, or quit.

    Args:
        config_path: Path to the maze configuration file (e.g.
            'config.txt').

    Raises:
        SystemExit: On configuration error or when the user selects
            'Quit' from the menu.
    """
    config = load_config(config_path)
    if config is None:
        print(
            "\033[91m[ERROR] Fix config.txt and restart "
            "the program.\033[0m"
        )
        sys.exit(1)

    def _handle_sigint(sig: int, frame: object) -> None:
        """Handle SIGINT (Ctrl-C) by clearing the screen and exiting."""
        clear_maze_display()
        sys.exit(0)

    signal.signal(signal.SIGINT, _handle_sigint)

    rows: int = int(str(config["rows"]))
    cols: int = int(str(config["cols"]))
    entry: tuple[int, int] = config["entry"]  # type: ignore[assignment]
    exit_: tuple[int, int] = config["exit"]   # type: ignore[assignment]
    perfect: bool = bool(config["perfect"])
    seed: Optional[int] = config["seed"]      # type: ignore[assignment]
    output_file: str = str(config["output_file"])

    logo_cells: set[tuple[int, int]] = get_logo_cells(rows, cols)

    logo_warning: Optional[str] = None
    if not logo_fits(rows, cols):
        min_h: int = _LOGO_H * 2 + 2
        min_w: int = (_LOGO_W4 + _LOGO_GAP + _LOGO_W2) * _LOGO_S + 2
        logo_warning = (
            f"\033[91m[ERROR] Maze too small for '42' logo "
            f"(need at least {min_w}x{min_h}, got {cols}x{rows}). "
            f"Logo omitted.\033[0m"
        )

    show_path: bool = False

    maze, carve_steps = generate_maze(
        rows, cols, entry, exit_, perfect, seed, logo_cells
    )
    path: list[tuple[int, int]] = find_path(maze, entry, exit_)
    write_maze_file(maze, path, entry, exit_, output_file)

    clear_maze_display()
    animate_generation(maze, carve_steps, logo_cells=logo_cells)
    animate_path(maze, path)
    show_path = True
    just_animated: bool = True
    flush_input()

    while True:
        if not just_animated:
            clear_maze_display()
            display_maze(
                maze,
                show_path=show_path,
                path=path,
                logo_cells=logo_cells,
            )
        just_animated = False

        if logo_warning:
            print(logo_warning)

        choice: str = display_menu()

        if choice == "1":
            new_seed: int = random.randint(0, 2 ** 32 - 1)
            maze, carve_steps = generate_maze(
                rows, cols, entry, exit_, perfect, new_seed, logo_cells
            )
            path = find_path(maze, entry, exit_)
            write_maze_file(maze, path, entry, exit_, output_file)
            clear_maze_display()
            animate_generation(
                maze, carve_steps, logo_cells=logo_cells
            )
            animate_path(maze, path)
            show_path = True
            just_animated = True
            flush_input()

        elif choice == "2":
            show_path = not show_path
            clear_maze_display()
            display_maze(
                maze,
                show_path=show_path,
                path=path,
                logo_cells=logo_cells,
            )
            just_animated = True

        elif choice == "3":
            rotate_wall_color()
            clear_maze_display()
            display_maze(
                maze,
                show_path=show_path,
                path=path,
                logo_cells=logo_cells,
            )
            just_animated = True

        else:
            clear_maze_display()
            break
