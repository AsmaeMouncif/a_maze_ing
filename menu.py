from display_maze import generate_maze, display_maze, solve_maze, rotate_wall_color, clear_maze_display


def display_menu():
    print("\n=== A_Maze_ing ===")
    print("1. Re-generate a new maze")
    print("2. Show/Hide path from entry to exit")
    print("3. Rotate maze colors")
    print("4. Quit")
    return input("Choice? (1-4): ")


maze = generate_maze()
path = solve_maze(maze)
show_path = False

display_maze(maze)

while True:
    choice = display_menu()

    if choice == "1":
        maze = generate_maze()
        path = solve_maze(maze)
        show_path = False
        clear_maze_display()
        display_maze(maze)

    elif choice == "2":
        show_path = not show_path
        clear_maze_display()
        display_maze(maze, show_path=show_path, path=path)

    elif choice == "3":
        rotate_wall_color()
        clear_maze_display()
        display_maze(maze, show_path=show_path, path=path)

    elif choice == "4":
        print("You've left the maze. See you next time!")
        break

    else:
        print("Invalid choice, please try again.")