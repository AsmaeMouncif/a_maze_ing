"""
output_writer.py — Write the maze to a file in hexadecimal wall format.

Output format (as required by the subject):
    - One hex digit per cell, rows separated by newlines.
    - Each digit encodes closed walls: bit0=North, bit1=East, bit2=South, bit3=West.
    - After an empty line: entry coords, exit coords, shortest path string.
"""

from maze_generator import MazeGenerator


def write_output(mg: MazeGenerator, output_file: str) -> None:
    """
    Write the maze to a file in the required hexadecimal format.

    Format:
        <row of hex digits>\\n
        ...
        \\n
        <entry_col>,<entry_row>\\n
        <exit_col>,<exit_row>\\n
        <path_string>\\n

    Args:
        mg:          A fully generated MazeGenerator instance.
        output_file: Path to the output file to write.

    Returns:
        None. Prints an error message if writing fails.
    """
    wall_grid = mg.get_wall_grid()
    entry = mg.get_entry()       # (row, col)
    exit_ = mg.get_exit()        # (row, col)
    path_str = mg.get_solution_string()

    try:
        with open(output_file, "w") as f:
            # Hex grid — one row per line
            for row in wall_grid:
                line = "".join(format(cell, 'X') for cell in row)
                f.write(line + "\n")

            # Empty separator line
            f.write("\n")

            # Entry: col,row
            f.write(f"{entry[1]},{entry[0]}\n")

            # Exit: col,row
            f.write(f"{exit_[1]},{exit_[0]}\n")

            # Shortest path
            f.write(path_str + "\n")

    except OSError as e:
        print(f"\033[91m[ERROR] Cannot write to '{output_file}': {e}\033[0m")