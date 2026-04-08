"""Logo pattern module for embedding the '42' pattern into the maze."""

_DIGIT_4: list[list[int]] = [
    [1, 0, 0],
    [1, 0, 0],
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 1],
]

_DIGIT_2: list[list[int]] = [
    [1, 1, 1],
    [0, 0, 1],
    [1, 1, 1],
    [1, 0, 0],
    [1, 1, 1],
]

_LOGO_H: int = 5
_LOGO_W4: int = 3
_LOGO_W2: int = 3
_LOGO_GAP: int = 1
_LOGO_S: int = 2


def logo_fits(rows: int, cols: int) -> bool:
    """Check whether the '42' logo fits within the given maze dimensions.

    Args:
        rows: Number of rows in the maze grid.
        cols: Number of columns in the maze grid.

    Returns:
        True if the logo can be drawn, False if the maze is too small.
    """
    return (
        rows >= _LOGO_H * _LOGO_S + 2
        and cols >= (_LOGO_W4 + _LOGO_GAP + _LOGO_W2) * _LOGO_S + 2
    )


def get_logo_cells(rows: int, cols: int) -> set[tuple[int, int]]:
    """Compute the set of maze cells that form the '42' logo pattern.

    The logo is centred inside the maze. Each digit is drawn at scale
    _LOGO_S (2x zoom) so that cells are clearly visible.

    Args:
        rows: Number of rows in the maze grid.
        cols: Number of columns in the maze grid.

    Returns:
        A set of (row, col) positions to keep as walls for the logo.
        Returns an empty set when the logo does not fit.
    """
    if not logo_fits(rows, cols):
        return set()

    s = _LOGO_S
    w4 = _LOGO_W4 * s
    w2 = _LOGO_W2 * s
    gap = _LOGO_GAP * s
    sh = _LOGO_H * s
    orig_r = (rows - sh) // 2
    orig_c = (cols - (w4 + gap + w2)) // 2

    logo: set[tuple[int, int]] = set()
    for grid, fw, col_off in [
        (_DIGIT_4, _LOGO_W4, 0),
        (_DIGIT_2, _LOGO_W2, w4 + gap),
    ]:
        for pr in range(_LOGO_H):
            for pc in range(fw):
                if grid[pr][pc] == 1:
                    for sr in range(s):
                        for sc in range(s):
                            r = orig_r + pr * s + sr
                            c = orig_c + col_off + pc * s + sc
                            if 1 <= r < rows - 1 and 1 <= c < cols - 1:
                                logo.add((r, c))
    return logo
