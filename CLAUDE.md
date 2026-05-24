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

## Dependencies
- All dependencies are managed via pyproject.toml and uv
- Never add defensive try/except imports for dependencies listed in pyproject.toml
- If a dependency is required, it should be properly declared and installed via `make deps`

## Markdown Syntax
- This blog uses Python-Markdown 3.8, which has slightly different syntax from GitHub Markdown
- **Important**: Bullet lists require a blank line before them to render properly
- See README.md for complete markdown syntax requirements and examples

## Article Frontmatter: Summary line
- The `Summary:` field is a short, descriptive one-liner — typically 8–15 words, almost always under ~20
- Plain descriptive prose, *not* a teaser, hook, or pitch. No em-dashes, no rhetorical setup, no quoted phrases from the post
- Written in third person / neutral voice ("How we handle X", "Why compilers do Y", "A look at Z") — not in the post's narrative voice
- Style to match: see existing posts, e.g. "Behind-the-scenes look at recording a CPU fundamentals series for Computerphile", "How we handle 92 million compilations a year without everything catching fire", "Compilers can rewrite loops to avoid expensive calculations"
- When in doubt, shorter is better. If it reads like a sentence from the post's opening paragraph, it's too long
