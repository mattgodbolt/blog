"""Tests for the date parser functionality."""

import datetime

import pytest
from pytz import timezone

from pygen.main import ParseDate, defaultTimeZone


def test_parse_basic_date():
    """Test parsing a basic date with no time component."""
    date = ParseDate("2020-01-01")
    # Just check the components, not the full datetime with timezone
    assert date.year == 2020
    assert date.month == 1
    assert date.day == 1
    assert date.hour == 0
    assert date.minute == 0
    assert date.second == 0
    assert str(date.tzinfo) == str(defaultTimeZone)


def test_parse_date_with_time():
    """Test parsing a date with time component."""
    date = ParseDate("2020-01-01 12:34:56")
    assert date.year == 2020
    assert date.month == 1
    assert date.day == 1
    assert date.hour == 12
    assert date.minute == 34
    assert date.second == 56
    assert str(date.tzinfo) == str(defaultTimeZone)


def test_parse_date_with_time_hours_only():
    """Test parsing a date with only hours specified."""
    date = ParseDate("2020-01-01 12")
    assert date.year == 2020
    assert date.month == 1
    assert date.day == 1
    assert date.hour == 12
    assert date.minute == 0
    assert date.second == 0
    assert str(date.tzinfo) == str(defaultTimeZone)


def test_parse_date_with_time_hours_minutes():
    """Test parsing a date with hours and minutes specified."""
    date = ParseDate("2020-01-01 12:34")
    assert date.year == 2020
    assert date.month == 1
    assert date.day == 1
    assert date.hour == 12
    assert date.minute == 34
    assert date.second == 0
    assert str(date.tzinfo) == str(defaultTimeZone)


def test_parse_date_with_whitespace():
    """Test parsing a date with extra whitespace."""
    date = ParseDate("  2020-01-01  12:34:56  ")
    assert date.year == 2020
    assert date.month == 1
    assert date.day == 1
    assert date.hour == 12
    assert date.minute == 34
    assert date.second == 56
    assert str(date.tzinfo) == str(defaultTimeZone)


def test_invalid_date_format():
    """Test that an invalid date format raises ValueError."""
    with pytest.raises(ValueError):
        ParseDate("not a date")


@pytest.mark.parametrize(
    "date_str,expected_components",
    [
        ("2020-01-01", (2020, 1, 1, 0, 0, 0)),
        ("2020-01-01 12", (2020, 1, 1, 12, 0, 0)),
        ("2020-01-01 12:34", (2020, 1, 1, 12, 34, 0)),
        ("2020-01-01 12:34:56", (2020, 1, 1, 12, 34, 56)),
    ],
)
def test_multiple_date_time_formats(date_str, expected_components):
    """Test various valid date time formats."""
    date = ParseDate(date_str)
    year, month, day, hour, minute, second = expected_components
    assert date.year == year
    assert date.month == month
    assert date.day == day
    assert date.hour == hour
    assert date.minute == minute
    assert date.second == second
    assert str(date.tzinfo) == str(defaultTimeZone)


# These tests will fail initially and should start passing when we implement timezone support
def test_date_with_offset_timezone():
    """Test parsing a date with a timezone offset like -0500."""
    date = ParseDate("2020-01-01 12:34:56 -0500")
    # Check if parsing succeeded and timezone is correctly set
    # We expect UTC-5 hours
    assert date.year == 2020
    assert date.month == 1
    assert date.day == 1
    assert date.hour == 12
    assert date.minute == 34
    assert date.second == 56
    # Check that it's not using the default timezone
    assert str(date.tzinfo) != str(defaultTimeZone)
    # A UTC-5 timezone should be 5 hours behind UTC
    utc_offset = date.tzinfo.utcoffset(date)
    assert utc_offset.total_seconds() == -5 * 60 * 60

    # Test a positive offset
    date = ParseDate("2020-01-01 12:34:56 +0100")
    # Check if parsing succeeded and timezone is correctly set
    assert date.year == 2020
    assert date.month == 1
    assert date.day == 1
    assert date.hour == 12
    assert date.minute == 34
    assert date.second == 56
    # A UTC+1 timezone should be 1 hour ahead of UTC
    utc_offset = date.tzinfo.utcoffset(date)
    assert utc_offset.total_seconds() == 1 * 60 * 60

    # Test with colon format
    date = ParseDate("2020-01-01 12:34:56 -05:00")
    # Check if parsing succeeded and timezone is correctly set
    assert date.year == 2020
    assert date.month == 1
    assert date.day == 1
    assert date.hour == 12
    assert date.minute == 34
    assert date.second == 56
    # A UTC-5 timezone should be 5 hours behind UTC
    utc_offset = date.tzinfo.utcoffset(date)
    assert utc_offset.total_seconds() == -5 * 60 * 60

    # Test positive offset with colon format
    date = ParseDate("2020-01-01 12:34:56 +01:00")
    # Check if parsing succeeded and timezone is correctly set
    assert date.year == 2020
    assert date.month == 1
    assert date.day == 1
    assert date.hour == 12
    assert date.minute == 34
    assert date.second == 56
    # A UTC+1 timezone should be 1 hour ahead of UTC
    utc_offset = date.tzinfo.utcoffset(date)
    assert utc_offset.total_seconds() == 1 * 60 * 60


def test_date_with_named_timezone():
    """Test parsing a date with a named timezone like America/Chicago."""
    date = ParseDate("2020-01-01 12:34:56 America/Chicago")
    # Check if parsing succeeded and timezone is correctly set
    assert date.year == 2020
    assert date.month == 1
    assert date.day == 1
    assert date.hour == 12
    assert date.minute == 34
    assert date.second == 56
    # Check that it's using the Chicago timezone
    chicago_tz = timezone("America/Chicago")
    assert str(date.tzinfo) == str(chicago_tz)


def test_common_us_timezone():
    """Test parsing a date with common US timezone."""
    date = ParseDate("2020-01-01 12:34:56 US/Central")
    # Check if parsing succeeded and timezone is correctly set
    assert date.year == 2020
    assert date.month == 1
    assert date.day == 1
    assert date.hour == 12
    assert date.minute == 34
    assert date.second == 56
    # Check that it's using the US/Central timezone
    central_tz = timezone("US/Central")
    assert str(date.tzinfo) == str(central_tz)


def test_invalid_timezone_name():
    """Test that invalid timezone names raise an error."""
    with pytest.raises(ValueError) as excinfo:
        ParseDate("2020-01-01 12:34:56 InvalidTimeZone")
    assert "Invalid timezone name" in str(excinfo.value)


def test_invalid_offset_timezone():
    """Test that invalid offset timezone format raises an error."""
    # Test offset with wrong format
    with pytest.raises(ValueError) as excinfo:
        ParseDate("2020-01-01 12:34:56 -5")  # Not enough digits
    assert "Invalid timezone name" in str(excinfo.value)
