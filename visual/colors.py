"""Color definitions and theme management for maze terminal display."""

RESET: str = "\033[0m"
PATH: str = "\033[48;5;232m" + "  " + RESET
BORDER: str = "  "

WALL_COLORS: list[tuple[str, str, str, str]] = [
    ("\033[48;5;22m",  "\033[48;5;121m",  "Green",  "Light Green"),
    ("\033[48;5;37m",  "\033[48;5;159m",  "Cyan",   "Light Cyan"),
    ("\033[48;5;20m",  "\033[48;5;153m",  "Blue",   "Light Blue"),
    ("\033[48;5;130m", "\033[48;5;223m",  "Gold",   "Light Peach"),
    ("\033[48;5;91m",  "\033[48;5;219m",  "Purple", "Light Pink"),
    ("\033[48;5;124m", "\033[48;5;217m",  "Red",    "Light Salmon"),
    ("\033[47m",       "\033[100m",       "White",  "Gray"),
]

current_color_index: int = 0


def get_wall() -> str:
    """Return the ANSI-colored string for a wall cell.

    Returns:
        A two-character string with background color for wall rendering.
    """
    return WALL_COLORS[current_color_index][0] + "  " + RESET


def get_trace() -> str:
    """Return the ANSI-colored string for a path trace cell.

    Returns:
        A two-character string with background color for path rendering.
    """
    return WALL_COLORS[current_color_index][1] + "  " + RESET


def get_entry() -> str:
    """Return the ANSI-colored string for the maze entry cell.

    Returns:
        A two-character string with background color for entry rendering.
    """
    return get_trace()


def get_exit() -> str:
    """Return the ANSI-colored string for the maze exit cell.

    Returns:
        A two-character string with background color for exit rendering.
    """
    return get_trace()


def rotate_wall_color() -> None:
    """Cycle to the next wall color theme.

    Rotates the global color index through all entries in WALL_COLORS.
    """
    global current_color_index
    current_color_index = (current_color_index + 1) % len(WALL_COLORS)
