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

default: serve