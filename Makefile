NAME = a_maze_ing.py
CONFIG = config.txt
PYTHON = python3

install:
	pip install -r requirements.txt

run:
	$(PYTHON) $(NAME) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(NAME) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

.PHONY: install run debug clean lint lint-strict