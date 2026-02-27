import random
import time
import sys
from collections import deque

RESET = "\033[0m"

ENTRY  = "\033[48;5;213m" + " " + RESET
EXIT   = "\033[48;5;196m" + " " + RESET
PATH   = "\033[48;5;232m" + " " + RESET
BORDER = " "

WALL_COLORS = [
    ("\033[47m",          "\033[100m",       "White",        "Gray"),
    ("\033[107m",         "\033[100m",       "Bright White",  "Gray"),
    ("\033[48;5;20m",     "\033[48;5;153m",  "Blue",          "Light Blue"),
    ("\033[48;5;37m",     "\033[48;5;159m",  "Cyan",          "Light Cyan"),
    ("\033[48;5;28m",     "\033[48;5;121m",  "Green",         "Light Green"),
    ("\033[48;5;130m",    "\033[48;5;223m",  "Gold",          "Light Peach"),
    ("\033[48;5;91m",     "\033[48;5;219m",  "Purple",        "Light Pink"),
    ("\033[48;5;124m",    "\033[48;5;217m",  "Dark Red",      "Light Salmon"),
]

current_color_index = 0

# Toujours 1 : on fait systematiquement clear_maze_display() avant display_maze()
# ce qui repositionne le curseur en (1,1).
MAZE_TOP_ROW = 1


def get_wall():
    return WALL_COLORS[current_color_index][0] + " " + RESET


def get_trace():
    return WALL_COLORS[current_color_index][1] + " " + RESET


def rotate_wall_color():
    global current_color_index
    current_color_index = (current_color_index + 1) % len(WALL_COLORS)


def clear_maze_display():
    # Efface l'ecran ET remet le curseur en (1,1)
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def generate_maze(rows=21, cols=21):
    maze = [['W' for _ in range(cols)] for _ in range(rows)]

    def carve(r, c):
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and maze[nr][nc] == 'W':
                maze[r + dr // 2][c + dc // 2] = ' '
                maze[nr][nc] = ' '
                carve(nr, nc)

    maze[1][1] = ' '
    carve(1, 1)
    maze[1][0] = 'E'
    maze[rows - 2][cols - 1] = 'X'

    return maze


def solve_maze(maze):
    rows = len(maze)
    cols = len(maze[0])

    start = end = None
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 'E':
                start = (r, c)
            elif maze[r][c] == 'X':
                end = (r, c)

    if not start or not end:
        return []

    queue = deque([[start]])
    visited = {start}

    while queue:
        path = queue.popleft()
        r, c = path[-1]

        if (r, c) == end:
            return path

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and (nr, nc) not in visited
                    and maze[nr][nc] != 'W'):
                visited.add((nr, nc))
                queue.append(path + [(nr, nc)])

    return []


def display_maze(maze, show_path=False, path=None):
    cols     = len(maze[0])
    wall     = get_wall()
    trace    = get_trace()
    path_set = set(path) if path else set()

    print(BORDER * (cols + 2))

    for r, row in enumerate(maze):
        line = BORDER
        for c, cell in enumerate(row):
            if cell == 'E':
                line += ENTRY
            elif cell == 'X':
                line += EXIT
            elif show_path and (r, c) in path_set:
                line += trace
            elif cell == 'W':
                line += wall
            else:
                line += PATH
        line += BORDER
        print(line)

    print(BORDER * (cols + 2))


def animate_path(maze, path, delay=0.03, stop_event=None):
    """Anime le chemin case par case avec positionnement absolu du curseur.

    Le labyrinthe commence toujours a la ligne 1 du terminal (apres un clear).
    - ligne 1          : bordure haute
    - ligne 2 + r      : rangee r du labyrinthe
    - colonne c + 2    : 1 espace de bordure gauche + position 1-indexee
    """
    trace = get_trace()

    for r, c in path:
        if stop_event is not None and stop_event.is_set():
            return

        if maze[r][c] in ('E', 'X'):
            continue

        term_row = MAZE_TOP_ROW + 1 + r   # ligne 1 (bordure) + 1 + r
        term_col = c + 2                   # bordure gauche + colonne 1-indexee

        sys.stdout.write(f"\033[s\033[{term_row};{term_col}f{trace}\033[u")
        sys.stdout.flush()
        time.sleep(delay)