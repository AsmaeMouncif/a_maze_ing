from maze_generator import MazeGenerator


def write_output(mg: MazeGenerator, output_file: str) -> None:
    wall_grid = mg.get_wall_grid()
    entry = mg.get_entry()
    exit_ = mg.get_exit()
    path_str = mg.get_solution_string()

    try:
        with open(output_file, "w") as f:
            for row in wall_grid:
                line = "".join(format(cell, 'X') for cell in row)
                f.write(line + "\n")

            f.write("\n")
            f.write(f"{entry[1]},{entry[0]}\n")
            f.write(f"{exit_[1]},{exit_[0]}\n")
            f.write(path_str + "\n")

    except OSError as e:
        print(f"\033[91m[ERROR] Cannot write to '{output_file}': {e}\033[0m")