"""Tests for the ETL templating functionality."""

import os
import tempfile

import pytest

from pygen.ETL import process_includes


def test_process_includes_basic():
    """Test that process_includes correctly includes template files."""
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an include file
        include_path = os.path.join(temp_dir, "header.html")
        with open(include_path, "w") as f:
            f.write("<header>Site Header</header>")

        # Create a main template file that includes the header
        template_path = os.path.join(temp_dir, "template.html")
        with open(template_path, "w") as f:
            f.write('<html><body>[%- include "header.html" -%]<main>Content</main></body></html>')

        # Process the template
        result, dependencies = process_includes(template_path, temp_dir)

        # Check that the include was processed correctly
        assert "<header>Site Header</header>" in result
        assert "<html><body><header>Site Header</header><main>Content</main></body></html>" == result

        # Check that dependencies are correctly tracked
        assert include_path in dependencies
        assert len(dependencies) == 1


def test_process_includes_nested():
    """Test that process_includes correctly handles nested includes."""
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create nested include files
        footer_path = os.path.join(temp_dir, "footer.html")
        with open(footer_path, "w") as f:
            f.write("<footer>Site Footer</footer>")

        layout_path = os.path.join(temp_dir, "layout.html")
        with open(layout_path, "w") as f:
            f.write('<div class="layout"><main>Content</main>[%- include "footer.html" -%]</div>')

        # Create a main template file that includes the layout
        template_path = os.path.join(temp_dir, "template.html")
        with open(template_path, "w") as f:
            f.write('<html><body>[%- include "layout.html" -%]</body></html>')

        # Process the template
        result, dependencies = process_includes(template_path, temp_dir)

        # Check that all includes were processed correctly
        assert "<footer>Site Footer</footer>" in result
        assert '<div class="layout"><main>Content</main><footer>Site Footer</footer></div>' in result
        assert (
            '<html><body><div class="layout"><main>Content</main><footer>Site Footer</footer></div></body></html>'
            == result
        )

        # Check that all dependencies are correctly tracked
        assert footer_path in dependencies
        assert layout_path in dependencies
        assert len(dependencies) == 2


def test_process_includes_multiple():
    """Test that process_includes correctly handles multiple includes."""
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple include files
        header_path = os.path.join(temp_dir, "header.html")
        with open(header_path, "w") as f:
            f.write("<header>Site Header</header>")

        footer_path = os.path.join(temp_dir, "footer.html")
        with open(footer_path, "w") as f:
            f.write("<footer>Site Footer</footer>")

        # Create a main template file with multiple includes
        template_path = os.path.join(temp_dir, "template.html")
        with open(template_path, "w") as f:
            f.write(
                '<html><body>[%- include "header.html" -%]<main>Content</main>[%- include "footer.html" -%]</body></html>'
            )

        # Process the template
        result, dependencies = process_includes(template_path, temp_dir)

        # Check that all includes were processed correctly
        assert "<header>Site Header</header>" in result
        assert "<footer>Site Footer</footer>" in result
        assert (
            "<html><body><header>Site Header</header><main>Content</main><footer>Site Footer</footer></body></html>"
            == result
        )

        # Check that all dependencies are correctly tracked
        assert header_path in dependencies
        assert footer_path in dependencies
        assert len(dependencies) == 2
