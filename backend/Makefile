# Hospital Management System - Development Commands

.PHONY: help install format lint test clean run dev

help: ## Show this help message
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt
	pre-commit install

format: ## Format code with Ruff
	ruff format .

lint: ## Lint code with Ruff
	ruff check .

lint-fix: ## Lint and fix code with Ruff
	ruff check --fix .

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term-missing

clean: ## Clean cache files
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov

run: ## Run the application
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

dev: ## Run in development mode
	uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

check: ## Run all checks (format, lint, test)
	make format
	make lint
	make test
