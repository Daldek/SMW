"""Tests for data providers."""

import pytest

from providers.parsers import parse_coordinates, parse_numeric_value


class TestParseNumericValue:
    """Tests for parse_numeric_value function."""

    def test_parse_integer(self):
        """Test parsing integer value."""
        value, flag = parse_numeric_value(42)
        assert value == 42.0
        assert flag is None

    def test_parse_float(self):
        """Test parsing float value."""
        value, flag = parse_numeric_value(3.14)
        assert value == 3.14
        assert flag is None

    def test_parse_string_number(self):
        """Test parsing numeric string."""
        value, flag = parse_numeric_value("12.5")
        assert value == 12.5
        assert flag is None

    def test_parse_string_with_comma(self):
        """Test parsing string with comma as decimal separator."""
        value, flag = parse_numeric_value("12,5")
        assert value == 12.5
        assert flag is None

    def test_parse_less_than_flag(self):
        """Test parsing value with less-than flag."""
        value, flag = parse_numeric_value("<0.05")
        assert value == 0.05
        assert flag == "<"

    def test_parse_greater_than_flag(self):
        """Test parsing value with greater-than flag."""
        value, flag = parse_numeric_value(">100")
        assert value == 100.0
        assert flag == ">"

    def test_parse_none(self):
        """Test parsing None value."""
        value, flag = parse_numeric_value(None)
        assert value is None
        assert flag is None

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        value, flag = parse_numeric_value("")
        assert value is None
        assert flag is None

    def test_parse_whitespace_string(self):
        """Test parsing whitespace string."""
        value, flag = parse_numeric_value("   ")
        assert value is None
        assert flag is None

    def test_parse_invalid_string(self):
        """Test parsing invalid string."""
        value, flag = parse_numeric_value("abc")
        assert value is None
        assert flag is None

    def test_parse_flag_with_comma(self):
        """Test parsing flag with comma decimal separator."""
        value, flag = parse_numeric_value("<0,05")
        assert value == 0.05
        assert flag == "<"


class TestParseCoordinates:
    """Tests for parse_coordinates function."""

    def test_parse_coordinates_with_dots(self):
        """Test parsing coordinates with dots."""
        lat, lon = parse_coordinates("52.2297 21.0122")
        assert lat == pytest.approx(52.2297)
        assert lon == pytest.approx(21.0122)

    def test_parse_coordinates_with_commas(self):
        """Test parsing coordinates with commas."""
        lat, lon = parse_coordinates("52,2297 21,0122")
        assert lat == pytest.approx(52.2297)
        assert lon == pytest.approx(21.0122)

    def test_parse_coordinates_with_semicolon(self):
        """Test parsing coordinates with semicolon separator."""
        lat, lon = parse_coordinates("52,2297;21,0122")
        assert lat == pytest.approx(52.2297)
        assert lon == pytest.approx(21.0122)

    def test_parse_coordinates_empty_string(self):
        """Test parsing empty string."""
        lat, lon = parse_coordinates("")
        assert lat is None
        assert lon is None

    def test_parse_coordinates_invalid_format(self):
        """Test parsing invalid format."""
        lat, lon = parse_coordinates("invalid")
        assert lat is None
        assert lon is None

    def test_parse_coordinates_non_string(self):
        """Test parsing non-string value."""
        lat, lon = parse_coordinates(123)
        assert lat is None
        assert lon is None

    def test_parse_coordinates_single_value(self):
        """Test parsing single value."""
        lat, lon = parse_coordinates("52.2297")
        assert lat is None
        assert lon is None
