import sys
import threading
from display_maze import (
    generate_maze, display_maze, solve_maze,
    rotate_wall_color, clear_maze_display, animate_path,
    load_config,
)


def display_menu():
    print("\n=== A_Maze_ing ===")
    print("1. Re-generate a new maze")
    print("2. Show/Hide path from entry to exit")
    print("3. Rotate maze colors")
    print("4. Quit")
    choice = input("Choice? (1-4): ")
    while choice not in ("1", "2", "3", "4"):
        sys.stdout.write("\033[1A\033[2K")
        sys.stdout.flush()
        choice = input("Choice? (1-4): ")
    return choice


# ─────────────────────────────────────────────
#  Animation thread management
# ─────────────────────────────────────────────

anim_thread     = None
anim_stop_event = None


def stop_animation():
    global anim_thread, anim_stop_event
    if anim_thread is not None and anim_thread.is_alive():
        anim_stop_event.set()
        anim_thread.join()
    anim_thread     = None
    anim_stop_event = None


def start_animation(maze, path):
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


# ─────────────────────────────────────────────
#  Startup: load config — exit on any error
# ─────────────────────────────────────────────

config = load_config()
if config is None:
    print("\033[91mFix config.txt and restart the program.\033[0m")
    sys.exit(1)

ROWS  = config["rows"]
COLS  = config["cols"]
ENTRY = config["entry"]   # (row, col)
EXIT  = config["exit"]    # (row, col)

maze      = generate_maze(rows=ROWS, cols=COLS, entry=ENTRY, exit_=EXIT)
path      = solve_maze(maze)
show_path = True

clear_maze_display()
display_maze(maze)
start_animation(maze, path)

# ─────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────

while True:
    choice = display_menu()

    if choice == "1":
        # Re-read config — exit immediately if it became invalid
        config = load_config()
        if config is None:
            stop_animation()
            print("\033[91mFix config.txt and restart the program.\033[0m")
            sys.exit(1)

        ROWS  = config["rows"]
        COLS  = config["cols"]
        ENTRY = config["entry"]
        EXIT  = config["exit"]

        stop_animation()
        maze      = generate_maze(rows=ROWS, cols=COLS, entry=ENTRY, exit_=EXIT)
        path      = solve_maze(maze)
        show_path = True
        clear_maze_display()
        display_maze(maze)
        start_animation(maze, path)

    elif choice == "2":
        stop_animation()
        clear_maze_display()
        display_maze(maze, show_path=False)

        if not show_path:
            show_path = True
            start_animation(maze, path)
        else:
            show_path = False

    elif choice == "3":
        stop_animation()
        rotate_wall_color()
        clear_maze_display()
        display_maze(maze, show_path=show_path, path=path)

    elif choice == "4":
        stop_animation()
        print("You've left the maze. See you next time!")
        break