RESET: str = "\033[0m"
PATH: str = "\033[48;5;232m" + "  " + RESET
BORDER: str = "  "


WALL_COLORS: list[tuple[str, str, str, str]] = [
    ("\033[48;5;22m",  "\033[48;5;121m",  "Green",    "Light Green"),
    ("\033[48;5;37m",  "\033[48;5;159m",  "Cyan",     "Light Cyan"),
    ("\033[48;5;20m",  "\033[48;5;153m",  "Blue",     "Light Blue"),
    ("\033[48;5;130m", "\033[48;5;223m",  "Gold",     "Light Peach"),
    ("\033[48;5;91m",  "\033[48;5;219m",  "Purple",   "Light Pink"),
    ("\033[48;5;124m", "\033[48;5;217m",  "Red",      "Light Salmon"),
    ("\033[47m",       "\033[100m",       "White",    "Gray"),
]

current_color_index: int = 0


def get_wall() -> str:
    return WALL_COLORS[current_color_index][0] + "  " + RESET


def get_trace() -> str:
    return WALL_COLORS[current_color_index][1] + "  " + RESET


def get_entry() -> str:
    return get_trace()


def get_exit() -> str:
    return get_trace()


def rotate_wall_color() -> None:
    global current_color_index
    current_color_index = (current_color_index + 1) % len(WALL_COLORS)
