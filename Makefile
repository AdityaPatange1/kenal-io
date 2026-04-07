.PHONY: build lint test validate clean install dev format examples run-tests

PYTHON ?= python3

install:
	$(PYTHON) -m pip install -e ".[dev]"

dev: install

build: clean
	$(PYTHON) -m build

lint:
	$(PYTHON) -m ruff check src/ tests/
	$(PYTHON) -m ruff format --check src/ tests/
	$(PYTHON) -m mypy src/kenal/

test:
	$(PYTHON) -m pytest tests/ -v --tb=short

examples:
	$(PYTHON) -u scripts/run_examples.py

run-tests:
	$(PYTHON) -u scripts/run_tests.py

validate: lint test
	@echo "All checks passed."

clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

format:
	$(PYTHON) -m ruff format src/ tests/
	$(PYTHON) -m ruff check --fix src/ tests/
