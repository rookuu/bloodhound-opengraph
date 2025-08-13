# Default target
help:
	@echo "Available targets:"

# Development setup
install:
	pip3 install -e .

install-dev:
	pip install -e ".[dev]"

# Testing targets
test:
	pytest tests/ -v --tb=short

# Build and release
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete