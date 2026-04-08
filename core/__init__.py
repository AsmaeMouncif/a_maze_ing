"""
Core package for the A-Maze-ing maze generator.

Provides three main functions:

- generate_maze: creates a maze grid and returns it with the ordered list of carved cells.
- find_path: solves the maze from entry to exit using BFS.
- write_maze_file: saves the maze and its solution to a text file.
"""

from core.maze_gen import generate_maze, find_path, write_maze_file

__all__ = [
    "generate_maze",
    "find_path",
    "write_maze_file",
]
