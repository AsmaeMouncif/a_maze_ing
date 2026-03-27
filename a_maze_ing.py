import sys
from maze_menu import run
sys.dont_write_bytecode = True


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "\033[91m[ERROR] Usage: python3 a_maze_ing.py config.txt\033[0m"
        )
        sys.exit(1)

    run(sys.argv[1])


if __name__ == "__main__":
    main()
