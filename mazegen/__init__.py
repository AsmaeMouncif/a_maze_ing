"""
mazegen — Reusable maze generator package.

Quick start::

    from mazegen import MazeGenerator

    # Create and generate a 21x15 perfect maze with seed 42
    gen = MazeGenerator(width=21, height=15, seed=42)
    gen.generate()

    # Solve it
    path = gen.solve()
    print(f"Path length: {len(path)} steps")
    print(f"Directions: {gen.path_directions()}")

    # Save to file
    gen.save("maze.txt")

    # Access the grid directly
    for row in gen.maze:
        print("".join(row))
"""

from mazegen.maze_generator import MazeGenerator

__all__ = ["MazeGenerator"]
__version__ = "1.0.0"
