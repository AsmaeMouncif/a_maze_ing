all: run

run:
	python3 a_maze_ing.py config.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

fclean: clean
	rm -f maze.txt

re: fclean run

lint:
	flake8 . --ignore-missing-imports
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . 
	mypy . --strict

.PHONY: all run clean fclean re lint lint-strict