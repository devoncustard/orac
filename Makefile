# OrAC — Development Makefile
# Usage: make <target>

.PHONY: all init test lint format docs serve docs-build clean help

SHELL := /bin/bash

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

init: ## Install dev dependencies
	@echo "Setting up OrAC dev environment..."
	python3 -m venv .venv
	.venv/bin/pip install -e ".[dev]"
	@echo "Done! Run '.venv/bin/orac --version' to verify."

test: ## Run tests
	.venv/bin/python -m pytest tests/unit/ -v --tb=short

test-cov: ## Run tests with coverage
	.venv/bin/python -m pytest tests/unit/ -v --cov=orac --cov-report=term-missing

lint: ## Run ruff linter
	.venv/bin/ruff check orac/ tests/

format: ## Format code with ruff
	.venv/bin/ruff format orac/ tests/

check: lint test ## Lint and test

docs: ## Serve docs locally
	mkdocs serve

docs-build: ## Build docs to site/
	mkdocs build

serve: docs ## Alias for docs

clean: ## Remove build artifacts
	rm -rf site/ .pytest_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
