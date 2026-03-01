import sys
import threading
from typing import Optional

from display_maze import (
    display_maze,
    rotate_wall_color,
    clear_maze_display,
    animate_path,
    animate_generation,
    load_config,
    MAZE_TOP_ROW,
)
from maze_generator import MazeGenerator
from output_writer import write_output


def build_maze(
    rows: int,
    cols: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    perfect: bool,
    seed: Optional[int],
) -> tuple[MazeGenerator, list[list[str]], list[tuple[int, int]], list[tuple[int, int]]]:
    mg = MazeGenerator(
        rows=rows,
        cols=cols,
        entry=entry,
        exit_=exit_,
        perfect=perfect,
        seed=seed,
    )
    grid = mg.get_grid()
    solution = mg.get_solution()
    carve_steps = mg.get_carve_steps()
    return mg, grid, solution, carve_steps


def display_menu() -> str:
    print("\n=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show/Hide path from entry to exit")
    print("3. Rotate maze colors")
    print("4. Quit")
    while True:
        choice = input("Choice? (1-4): ").strip()
        if choice in ("1", "2", "3", "4"):
            return choice
        print("Invalid choice. Please enter 1, 2, 3, or 4.")


anim_thread: Optional[threading.Thread] = None
anim_stop_event: Optional[threading.Event] = None


def stop_animation() -> None:
    global anim_thread, anim_stop_event
    if anim_thread is not None and anim_thread.is_alive():
        if anim_stop_event is not None:
            anim_stop_event.set()
        anim_thread.join()
    anim_thread = None
    anim_stop_event = None


def start_animation(
    maze: list[list[str]],
    path: list[tuple[int, int]],
) -> None:
    global anim_thread, anim_stop_event
    stop_animation()
    anim_stop_event = threading.Event()
    anim_thread = threading.Thread(
        target=animate_path,
        args=(maze, path),
        kwargs={"stop_event": anim_stop_event},
        daemon=True,
    )
    anim_thread.start()


if len(sys.argv) != 2:
    print("\033[91m[ERROR] Usage: python3 a_maze_ing.py config.txt\033[0m")
    sys.exit(1)

config = load_config(sys.argv[1])
if config is None:
    print("\033[91mFix config.txt and restart the program.\033[0m")
    sys.exit(1)

ROWS: int = config["rows"]
COLS: int = config["cols"]
ENTRY: tuple[int, int] = config["entry"]
EXIT: tuple[int, int] = config["exit"]
PERFECT: bool = config["perfect"]
SEED: Optional[int] = config["seed"]
OUTPUT_FILE: str = config["output_file"]

mg, maze, path, carve_steps = build_maze(ROWS, COLS, ENTRY, EXIT, PERFECT, SEED)
write_output(mg, OUTPUT_FILE)

show_path: bool = True
animate_generation(maze, carve_steps)
rows_count = len(maze)
sys.stdout.write(f"\033[{MAZE_TOP_ROW + rows_count + 2};1H")
sys.stdout.flush()
start_animation(maze, path)

while True:
    choice = display_menu()

    if choice == "1":
        config = load_config(sys.argv[1])
        if config is None:
            stop_animation()
            print("\033[91mFix config.txt and restart the program.\033[0m")
            sys.exit(1)

        ROWS = config["rows"]
        COLS = config["cols"]
        ENTRY = config["entry"]
        EXIT = config["exit"]
        PERFECT = config["perfect"]
        SEED = None
        OUTPUT_FILE = config["output_file"]

        stop_animation()
        mg, maze, path, carve_steps = build_maze(ROWS, COLS, ENTRY, EXIT, PERFECT, SEED)
        write_output(mg, OUTPUT_FILE)
        show_path = True
        animate_generation(maze, carve_steps)
        rows_count = len(maze)
        sys.stdout.write(f"\033[{MAZE_TOP_ROW + rows_count + 2};1H")
        sys.stdout.flush()
        start_animation(maze, path)

    elif choice == "2":
        stop_animation()
        show_path = not show_path
        clear_maze_display()
        if show_path:
            display_maze(maze, show_path=True, path=path)
            start_animation(maze, path)
        else:
            display_maze(maze, show_path=False)

    elif choice == "3":
        stop_animation()
        rotate_wall_color()
        clear_maze_display()
        display_maze(maze, show_path=show_path, path=path if show_path else None)

    elif choice == "4":
        stop_animation()
        print("You've left the maze. See you next time!")
        break