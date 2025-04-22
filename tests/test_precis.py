"""Tests for the article summarization functionality."""

import xml.etree.ElementTree as ET

import pytest

from pygen.precis import PrecisProcessor


def create_mock_markdown_processor():
    """Create a mock Markdown processor for testing."""

    class MockMarkdown:
        pass

    return MockMarkdown()


def test_precis_processor_short_article():
    """Test that the PrecisProcessor preserves short articles."""
    # Create a PrecisProcessor instance
    md = create_mock_markdown_processor()
    processor = PrecisProcessor(md)

    # Create a short test document with fewer than 5 paragraphs
    root = ET.Element("root")
    for i in range(4):
        p = ET.SubElement(root, "p")
        p.text = f"Paragraph {i+1}"

    # Run the processor
    result = processor.run(root)

    # Check that all paragraphs are preserved (since it's a short article)
    assert len(result) == 4
    for i, child in enumerate(result):
        assert child.tag == "p"
        assert child.text == f"Paragraph {i+1}"


def test_precis_processor_long_article():
    """Test that the PrecisProcessor truncates long articles."""
    # Create a PrecisProcessor instance
    md = create_mock_markdown_processor()
    processor = PrecisProcessor(md)

    # Create a longer test document with more than 5 paragraphs
    root = ET.Element("root")
    for i in range(10):
        p = ET.SubElement(root, "p")
        p.text = f"Paragraph {i+1}"

    # Run the processor
    result = processor.run(root)

    # Check that only the first 3 paragraphs are preserved
    assert len(result) == 3
    for i, child in enumerate(result):
        assert child.tag == "p"
        assert child.text == f"Paragraph {i+1}"


def test_precis_processor_mixed_content():
    """Test that the PrecisProcessor correctly handles mixed content."""
    # Create a PrecisProcessor instance
    md = create_mock_markdown_processor()
    processor = PrecisProcessor(md)

    # Create a test document with mixed content
    root = ET.Element("root")
    ET.SubElement(root, "h1").text = "Title"
    ET.SubElement(root, "h2").text = "Subtitle"
    for i in range(8):
        if i == 2:
            # Add a non-paragraph element in the middle
            ET.SubElement(root, "ul").text = "List item"
        else:
            p = ET.SubElement(root, "p")
            p.text = f"Paragraph {i+1}"

    # Run the processor
    result = processor.run(root)

    # Check that the first elements are preserved
    assert result[0].tag == "h1"
    assert result[0].text == "Title"
    assert result[1].tag == "h2"
    assert result[1].text == "Subtitle"

    # Count how many paragraphs remain
    p_count = sum(1 for child in result if child.tag == "p")

    # Since there are more than 5 paragraphs originally,
    # should limit to 3 paragraphs (per the implementation)
    assert p_count <= 3
