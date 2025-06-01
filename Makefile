SHELL := $(shell which bash) # Use bash instead of bin/sh as shell

.PHONY: help
help: ## Show this help
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

ifndef VERBOSE
.SILENT:
endif

.PHONY: check-uv
check-uv:
	@if ! command -v uv &> /dev/null; then \
		echo "Error: uv is not installed. Please install it from https://docs.astral.sh/uv/getting-started/installation/"; \
		exit 1; \
	fi

.PHONY: deps
deps: check-uv ## Install dependencies
	uv sync --extra dev

.PHONY: pre-commit-install
pre-commit-install: deps ## Install pre-commit hooks
	uv run pre-commit install

.PHONY: lint
lint: deps ## Run all linters (warnings only)
	uv run pre-commit run --all-files

.PHONY: lint-staged
lint-staged: deps ## Run linters on staged files
	uv run pre-commit run

.PHONY: format-black
format-black: deps ## Format Python files with black
	uv run black pygen serve.py

.PHONY: format-isort
format-isort: deps ## Sort imports with isort
	uv run isort pygen serve.py

.PHONY: lint-fix
lint-fix: format-black format-isort ## Fix formatting and imports
	uv run ruff check --fix pygen serve.py

.PHONY: format
format: lint-fix ## Alias for lint-fix

.PHONY: update
update: deps ## Generate site content
	mkdir -p www/feed
	uv run python -m pygen.main

.PHONY: publish
publish: update ## Build and publish to S3
	./publish.sh

.PHONY: serve
serve: ## Run development server
	uv run python ./serve.py

.PHONY: test
test: deps ## Run tests
	uv run pytest

default: serve
