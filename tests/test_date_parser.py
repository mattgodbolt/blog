"""Tests for the date parser functionality."""

import datetime

import pytest
from pytz import timezone, utc

from pygen.main import FormatAtomDates, FormatHtmlDate, FormatISODate, ParseDate, defaultTimeZone


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


def test_dst_handling():
    """Test parsing dates near DST transitions."""
    # Test a valid time (not in DST transition)
    date = ParseDate("2023-03-11 02:30:00 US/Pacific")
    assert date.year == 2023
    assert date.month == 3
    assert date.day == 11
    assert date.hour == 2
    assert date.minute == 30

    # Test a time after DST starts
    date = ParseDate("2023-03-12 03:30:00 US/Pacific")
    assert date.year == 2023
    assert date.month == 3
    assert date.day == 12
    assert date.hour == 3
    assert date.minute == 30

    # Test the offset timezone handling instead of named timezone for non-DST date
    date = ParseDate("2023-11-05 01:30:00 -0800")  # PST offset
    assert date.year == 2023
    assert date.month == 11
    assert date.day == 5
    assert date.hour == 1
    assert date.minute == 30
    # -0800 is 8 hours behind UTC
    utc_offset = date.tzinfo.utcoffset(date)
    assert utc_offset.total_seconds() == -8 * 60 * 60


def test_format_iso_date():
    """Test ISO date formatting converts to UTC."""
    # Create a date in US/Pacific timezone
    pacific_tz = timezone("US/Pacific")
    local_date = pacific_tz.localize(datetime.datetime(2023, 1, 15, 14, 30, 0))

    # Format as ISO date (should convert to UTC)
    iso_date = FormatISODate(local_date)

    # US/Pacific is UTC-8 in January, so 14:30 should become 22:30 UTC
    assert "2023-01-15T22:30:00Z" in iso_date


def test_format_html_date():
    """Test HTML date formatting preserves timezone."""
    # Create a date in Europe/Paris timezone
    paris_tz = timezone("Europe/Paris")
    local_date = paris_tz.localize(datetime.datetime(2023, 6, 1, 14, 30, 0))

    # Format as HTML date
    html_date = FormatHtmlDate(local_date)

    # Check time and timezone are in the output
    assert "14:30:00" in html_date
    assert "CEST" in html_date or "CET" in html_date
    # Check date formatting
    assert "1<sup>st</sup> June 2023" in html_date


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


def test_timezone_conversion():
    """Test conversion between different timezones."""
    # Create a date in Tokyo timezone
    tokyo_tz = timezone("Asia/Tokyo")
    tokyo_date = tokyo_tz.localize(datetime.datetime(2023, 1, 1, 12, 0, 0))

    # Convert to New York timezone
    nyc_tz = timezone("America/New_York")
    nyc_date = tokyo_date.astimezone(nyc_tz)

    # Tokyo is UTC+9, New York is UTC-5 in January
    # 12:00 in Tokyo should be 22:00 previous day in New York
    assert nyc_date.year == 2022
    assert nyc_date.month == 12
    assert nyc_date.day == 31
    assert nyc_date.hour == 22
    assert nyc_date.minute == 0


def test_parse_date_leap_year():
    """Test parsing dates in leap years."""
    # February 29 in a leap year
    date = ParseDate("2020-02-29")
    assert date.year == 2020
    assert date.month == 2
    assert date.day == 29

    # February 29 in a leap year with timezone
    date = ParseDate("2020-02-29 12:00:00 US/Pacific")
    assert date.year == 2020
    assert date.month == 2
    assert date.day == 29
    assert date.hour == 12
    assert date.minute == 0
    pacific_tz = timezone("US/Pacific")
    assert str(date.tzinfo) == str(pacific_tz)


def test_compare_dates_different_timezones():
    """Test comparing dates in different timezones."""
    # Same time in different timezones
    london_tz = timezone("Europe/London")
    nyc_tz = timezone("America/New_York")

    london_date = london_tz.localize(datetime.datetime(2023, 1, 1, 17, 0, 0))
    nyc_date = nyc_tz.localize(datetime.datetime(2023, 1, 1, 12, 0, 0))

    # Same instant in time, despite different local times
    # NYC is 5 hours behind London in January
    assert london_date.astimezone(utc) == nyc_date.astimezone(utc)

    # Test date comparison directly
    # These should be the same point in time
    assert london_date == nyc_date
