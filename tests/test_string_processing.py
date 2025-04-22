"""Tests for the string processing functionality."""

import pytest

from pygen.main import ProcessTitle, XHtmlToHtml


def test_process_title_escapes_html_entities():
    """Test that ProcessTitle properly escapes HTML entities in titles."""
    # Test with ampersand
    title = "Title with & ampersand"
    processed = ProcessTitle(title)
    assert processed == "Title with &amp; ampersand"

    # Test with less than and greater than symbols
    title = "Title with <tag> brackets"
    processed = ProcessTitle(title)
    assert processed == "Title with &lt;tag&gt; brackets"

    # Test with all special characters
    title = "Title with <tag> & ampersand"
    processed = ProcessTitle(title)
    assert processed == "Title with &lt;tag&gt; &amp; ampersand"


def test_xhtml_to_html_conversion():
    """Test that XHtmlToHtml properly converts self-closing tags."""
    # Test with self-closing hr tag
    xhtml = "<p>Text</p><hr/><p>More text</p>"
    html = XHtmlToHtml(xhtml)
    assert html == "<p>Text</p><hr><p>More text</p>"

    # Test with self-closing br tag
    xhtml = "<p>Line 1<br/>Line 2</p>"
    html = XHtmlToHtml(xhtml)
    assert html == "<p>Line 1<br>Line 2</p>"

    # Test with img tag and attributes
    xhtml = '<p><img src="image.jpg" alt="Image"/></p>'
    html = XHtmlToHtml(xhtml)
    assert html == '<p><img src="image.jpg" alt="Image"></p>'

    # Test with param tag
    xhtml = '<object><param name="value" value="10"/></object>'
    html = XHtmlToHtml(xhtml)
    assert html == '<object><param name="value" value="10"></object>'

    # Test with multiple tags
    xhtml = "<p>Text<br/>More<hr/>End</p>"
    html = XHtmlToHtml(xhtml)
    assert html == "<p>Text<br>More<hr>End</p>"

    # Test with non-breaking spaces
    xhtml = "<p>Text&nbsp;with&nbsp;spaces</p>"
    html = XHtmlToHtml(xhtml)
    assert html == "<p>Text&#160;with&#160;spaces</p>"
