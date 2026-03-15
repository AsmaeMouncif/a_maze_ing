import sys
import os
import termios


def get_terminal_size() -> tuple[int, int]:
    try:
        s = os.get_terminal_size()
        return s.columns, s.lines
    except OSError:
        return 80, 24


def check_terminal_size(maze_rows: int, maze_cols: int) -> None:
    term_cols, term_rows = get_terminal_size()
    need_cols = maze_cols * 2 + 4
    need_rows = maze_rows + 6

    if term_cols >= need_cols and term_rows >= need_rows:
        return

    print("\033[91m[ERROR] Your terminal is too small to display this maze.\033[0m")
    print("\033[91mPlease resize your terminal or reduce WIDTH/HEIGHT in config.txt.\033[0m")
    sys.exit(1)


def clear_maze_display() -> None:
    try:
        print("\033[2J", end="")
        print("\033[3J", end="")
        print("\033[H", end="")
        sys.stdout.flush()
    except Exception:
        pass

def flush_input() -> None:
    try:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except Exception:
        pass
