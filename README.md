# Matt Godbolt's Personal Blog

My personal blog and website files, served at [xania.org](https://xania.org/).

**Note:** This repository is primarily for my personal use and reference. While it's public, it's not intended as a general-purpose blogging platform.

## Project Overview

This is a static site generator for my blog that:
- Processes Markdown articles with metadata headers
- Generates HTML using custom templates
- Publishes content to AWS S3

## Article Format

Articles are stored in the `www/article/` directory, organized by date (YYYYMM) folders. Each article is a `.text` file with the following format:

```
Title of the Article
Date: YYYY-MM-DD HH:MM:SS
Label: Category1, Category2
Status: Public
Summary: A brief description of the article content

The article content in Markdown format begins here.
This can include **bold text**, *italics*, and [links](https://example.com).

Images can be included using Markdown syntax:
![Alt text](path/to/image.png)

Or with HTML for more control:
<p class="picture">
  <img src="path/to/image.png" alt="Alt text">
  <br>Caption for the image
</p>

Code blocks use triple backticks:
```python
def hello_world():
    print("Hello, world!")
```

## Markdown Syntax Requirements

This blog uses **Python-Markdown 3.8** with extensions. The syntax is mostly standard Markdown, but has some specific requirements:

### Bullet Lists

**Important**: Lists require a **blank line before them** to render properly:

```markdown
Text before the list:

- Item 1  ← Note the blank line above
- Item 2
- Item 3
```

**Won't work:**
```markdown
Text directly followed by:
- Item 1  ← Missing blank line above
```

### Nested Lists

Use exactly **4 spaces** for nested items:

```markdown
* Main item:
    - Sub item (4 spaces)
    - Another sub item
        - Nested deeper (8 spaces)
```

### Other List Requirements

- Always include a space after the bullet character: `- Item` not `-Item`
- All bullet characters work: `-`, `*`, and `+`
- Mix bullet types if desired, but be consistent within each level

### Header Fields

- **Title**: The first line of the file (no explicit key)
- **Date**: Publication date and time in one of these formats:
  - `YYYY-MM-DD` - Uses default timezone (Europe/London)
  - `YYYY-MM-DD HH` - Only hour specified, uses default timezone
  - `YYYY-MM-DD HH:MM` - Hour and minute, uses default timezone
  - `YYYY-MM-DD HH:MM:SS` - Full timestamp, uses default timezone
  - `YYYY-MM-DD HH:MM:SS TZNAME` - With named timezone (e.g., America/Chicago, US/Central)
  - `YYYY-MM-DD HH:MM:SS ±HHMM` - With timezone offset (e.g., -0500, +0100)
  - `YYYY-MM-DD HH:MM:SS ±HH:MM` - With timezone offset with colon (e.g., -05:00, +01:00)
- **Label**: Category tags for the article (comma-separated)
- **Status** (optional): Typically "Public"
- **Summary** (optional): Brief description for previews/metadata

After the header fields and a blank line, the article content follows in Markdown format.

## Build & Run Commands

- **Setup**: `make deps` - Installs Poetry locally and sets up dependencies
- **Generate site**: `make update` - Rebuilds blog content
- **Preview locally**: `make serve` - Builds and serves site at localhost:8000
- **Publish to S3**: `make publish` - Builds and deploys to production

### Development Commands

- **Install pre-commit hooks**: `make pre-commit-install` - Sets up git hooks
- **Run linters**: `make lint` - Runs pre-commit hooks on all files
- **Fix formatting**: `make format` - Formats Python files and fixes issues

The project uses Poetry for dependency management. The Makefile automatically installs Poetry locally in the `.poetry` directory and manages the virtual environment for you.

## Project Structure

- `pygen/`: Main Python generation code (Python package)
- `conf/`: Templates and configuration
- `www/`: Website content and generated files
- `publish.sh`: Deployment script for AWS S3
- `pyproject.toml`: Poetry configuration and dependencies
- `poetry.lock`: Locked dependency versions for reproducible builds

## Potential Improvements

### High Priority
1. ✅ **Move to Poetry for dependency management** (Completed)
   - ✅ Replace `requirements.txt` with `pyproject.toml`
   - ✅ Add proper dependency versioning and lock file

2. **Modernize Python code**
   - Add type hints
   - Use f-strings consistently
   - Remove Python 2.x compatibility code

3. **Replace custom ETL templating with Jinja2**
   - More maintainable and familiar template syntax
   - Better error reporting and debugging

### Medium Priority
4. ✅ **Development workflow improvements** (Partially completed)
   - ✅ Add linting and formatting tools
   - ✅ Create pre-commit hooks
   - Add GitHub Actions for CI/CD

5. ✅ **Remove caching system** (Completed)
   - ✅ Removed unnecessary caching layer
   - ✅ Simplified article processing workflow

6. **Add tests**
   - ✅ Unit tests for date parsing functionality
   - ✅ Unit tests for date formatting
   - ✅ Unit tests for string processing
   - ✅ Unit tests for ETL template system
   - ✅ Unit tests for article summarization (precis)
   - Integration tests for site generation

7. **Configuration management**
   - Consider moving from custom format to YAML/TOML

8. **Content authoring improvements**
   - Article preview/draft functionality
   - Better image management tools
   - Live preview while editing

9. **Documentation improvements**
   - Add inline documentation to Python code
   - Document the custom ETL templating system
   - Add comments for complex logic

## Implementation Strategy

A suggested sequence for implementing the improvements:

1. **Initial modernization**
   - ✅ Set up Poetry for dependency management
   - ✅ Add basic linting and formatting
   - Document existing code before changing it

2. **Core improvements**
   - ✅ Remove the caching system
   - Modernize Python code (type hints, f-strings)
   - Add tests for critical functionality

3. **Template system migration**
   - Document the current ETL system
   - Gradually replace with Jinja2
   - Update templates one by one

4. **Workflow and UI improvements**
   - Enhance development workflow
   - Implement content authoring improvements
   - Consider frontend modernization where beneficial
