# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands
- Setup: `make deps` - Creates venv and installs requirements
- Generate site: `make update` - Rebuilds blog content
- Preview locally: `make serve` - Builds and serves site at localhost:8000
- Publish to S3: `make publish` - Builds and deploys to production

## Code Style
- Python: Follow PEP 8 guidelines
- Indentation: 4 spaces
- Line length: < 120 characters
- Function naming: snake_case
- Class naming: PascalCase
- Error handling: Use try/except blocks with specific exceptions
- Variable names: Descriptive, avoid abbreviations
- For ETL templates: Use consistent spacing for template variables
- **Spelling: Always use British English spellings** (favourite not favorite, colour not color, realise not realize, optimise not optimize, centre not center, etc.)

## Development Workflow
- Always run `pre-commit run --all-files` before running `git add` to ensure code formatting
- Use `make lint` to check for linting issues
- Use `make format` to fix formatting issues
- Use `make test` to run the test suite
- Let the formatter make its changes before committing code
- All tests must pass before creating a PR

## Project Structure
- pygen/: Main Python generation code
- conf/: Templates and configuration
- www/: Website content and generated files
- Article format: Markdown with YAML-like headers
