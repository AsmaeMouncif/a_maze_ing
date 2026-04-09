"""Terminal utility functions for display management."""

import sys
import os
import termios


def get_terminal_size() -> tuple[int, int]:
    """Retrieve the current terminal dimensions.

    Returns:
        A tuple (columns, lines) representing terminal size.
        Defaults to (80, 24) if the size cannot be determined.
    """
    try:
        s = os.get_terminal_size()
        return s.columns, s.lines
    except OSError:
        return 80, 24


def check_terminal_size(maze_rows: int, maze_cols: int) -> None:
    """Verify the terminal is large enough to display the maze.

    Args:
        maze_rows: Number of rows in the maze grid.
        maze_cols: Number of columns in the maze grid.

    Raises:
        SystemExit: If the terminal is too small to display the maze.
    """
    term_cols, term_rows = get_terminal_size()
    need_cols = maze_cols * 2 + 4
    need_rows = maze_rows + 7

    if term_cols >= need_cols and term_rows >= need_rows:
        return

    print(
        "\033[91m[ERROR] Your terminal is too small "
        "to display this maze.\033[0m"
    )
    print(
        "\033[91mPlease resize your terminal or reduce "
        "WIDTH/HEIGHT in config.txt.\033[0m"
    )
    sys.exit(1)


def clear_maze_display() -> None:
    """Clear the terminal screen and reset the cursor to the top-left."""
    try:
        # \033[2J clears the visible screen
        # \033[3J clears the scrollback buffer (the history you can scroll up)
        # \033[H moves the cursor to the top-left corner (line 1, column 1)

        # Send all escape codes to the terminal
        sys.stdout.write("\033[2J\033[3J\033[H")
        sys.stdout.flush()
    except OSError:
        pass


def flush_input() -> None:
    """Clear any pending keystrokes from stdin to prevent accidental input
    during animations or delays."""
    try:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)  # type: ignore
    except Exception:
        pass
