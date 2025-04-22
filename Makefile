SHELL := $(shell which bash) # Use bash instead of bin/sh as shell
SYS_PYTHON := $(shell which python3 || echo ".python_is_missing")
export POETRY_HOME=$(CURDIR)/.poetry
POETRY := $(POETRY_HOME)/bin/poetry
VENV := $(CURDIR)/.venv
PYTHON := $(VENV)/bin/python
DEPS := $(VENV)/.deps

.PHONY: help
help: ## Show this help
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

ifndef VERBOSE
.SILENT:
endif

$(SYS_PYTHON):
	@echo "You need Python 3. I can't find it on the PATH."
	@false

$(POETRY): $(SYS_PYTHON)
	curl -sSL https://install.python-poetry.org | $(SYS_PYTHON) -

$(VENV): $(POETRY)
	$(SYS_PYTHON) -m venv $(VENV)

$(DEPS): pyproject.toml poetry.lock | $(VENV)
	$(POETRY) install --sync
	cp pyproject.toml $(DEPS)

.PHONY: deps
deps: $(DEPS) ## Install dependencies

.PHONY: pre-commit-install
pre-commit-install: deps ## Install pre-commit hooks
	pre-commit install

.PHONY: lint
lint: deps ## Run all linters (warnings only)
	pre-commit run --all-files

.PHONY: lint-staged
lint-staged: deps ## Run linters on staged files
	pre-commit run

.PHONY: format-black
format-black: deps ## Format Python files with black
	$(POETRY) run black pygen serve.py

.PHONY: format-isort
format-isort: deps ## Sort imports with isort
	$(POETRY) run isort pygen serve.py

.PHONY: lint-fix
lint-fix: format-black format-isort ## Fix formatting and imports
	$(POETRY) run ruff check --fix pygen serve.py

.PHONY: format
format: lint-fix ## Alias for lint-fix

.PHONY: update
update: deps ## Generate site content
	mkdir -p www/feed
	$(POETRY) run python -m pygen.main

.PHONY: publish
publish: update ## Build and publish to S3
	./publish.sh

.PHONY: serve
serve: update ## Run development server
	$(POETRY) run python ./serve.py

.PHONY: test
test: deps ## Run tests
	$(POETRY) run pytest

default: serve
