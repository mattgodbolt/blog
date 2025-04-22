"""Tests for the date formatting functionality."""

import datetime

import pytest
from pytz import timezone, utc

from pygen.main import FormatAtomDates, FormatHtmlDate, FormatISODate


def test_format_html_date_with_ordinal_suffixes():
    """Test that FormatHtmlDate properly formats dates with correct ordinal suffixes."""
    # Test 1st suffix
    london_tz = timezone("Europe/London")
    date = london_tz.localize(datetime.datetime(2023, 5, 1, 14, 30, 0))
    html_date = FormatHtmlDate(date)
    assert "1<sup>st</sup>" in html_date

    # Test 2nd suffix
    date = london_tz.localize(datetime.datetime(2023, 5, 2, 14, 30, 0))
    html_date = FormatHtmlDate(date)
    assert "2<sup>nd</sup>" in html_date

    # Test 3rd suffix
    date = london_tz.localize(datetime.datetime(2023, 5, 3, 14, 30, 0))
    html_date = FormatHtmlDate(date)
    assert "3<sup>rd</sup>" in html_date

    # Test 4th (th) suffix
    date = london_tz.localize(datetime.datetime(2023, 5, 4, 14, 30, 0))
    html_date = FormatHtmlDate(date)
    assert "4<sup>th</sup>" in html_date

    # Test 11th (th) suffix (special case)
    date = london_tz.localize(datetime.datetime(2023, 5, 11, 14, 30, 0))
    html_date = FormatHtmlDate(date)
    assert "11<sup>th</sup>" in html_date

    # Test 21st suffix
    date = london_tz.localize(datetime.datetime(2023, 5, 21, 14, 30, 0))
    html_date = FormatHtmlDate(date)
    assert "21<sup>st</sup>" in html_date


def test_format_html_date_includes_time_zone():
    """Test that FormatHtmlDate includes the time and timezone."""
    # Test with London timezone
    london_tz = timezone("Europe/London")
    date = london_tz.localize(datetime.datetime(2023, 1, 15, 14, 30, 0))
    html_date = FormatHtmlDate(date)
    assert "14:30:00" in html_date
    assert "GMT" in html_date or "BST" in html_date

    # Test with Pacific timezone
    pacific_tz = timezone("US/Pacific")
    date = pacific_tz.localize(datetime.datetime(2023, 1, 15, 14, 30, 0))
    html_date = FormatHtmlDate(date)
    assert "14:30:00" in html_date
    assert "PST" in html_date or "PDT" in html_date


def test_format_iso_date():
    """Test that FormatISODate properly formats dates in ISO format with UTC timezone."""
    # Test with UTC timezone
    date = utc.localize(datetime.datetime(2023, 1, 15, 14, 30, 0))
    iso_date = FormatISODate(date)
    assert iso_date == "2023-01-15T14:30:00Z"

    # Test with non-UTC timezone (should convert to UTC)
    pacific_tz = timezone("US/Pacific")
    date = pacific_tz.localize(datetime.datetime(2023, 1, 15, 6, 30, 0))  # 6:30 PST = 14:30 UTC
    iso_date = FormatISODate(date)
    assert iso_date == "2023-01-15T14:30:00Z"


def test_format_atom_dates_single_date():
    """Test that FormatAtomDates properly formats a single date."""
    date = utc.localize(datetime.datetime(2023, 1, 15, 14, 30, 0))
    atom_date = FormatAtomDates([date])
    expected = "<updated>2023-01-15T14:30:00Z</updated>"
    assert atom_date == expected


def test_format_atom_dates_multiple_dates():
    """Test that FormatAtomDates properly formats multiple dates."""
    date1 = utc.localize(datetime.datetime(2023, 1, 15, 14, 30, 0))
    date2 = utc.localize(datetime.datetime(2023, 1, 16, 10, 0, 0))

    atom_date = FormatAtomDates([date1, date2])
    expected1 = "<published>2023-01-15T14:30:00Z</published>"
    expected2 = "<updated>2023-01-16T10:00:00Z</updated>"

    assert expected1 in atom_date
    assert expected2 in atom_date
