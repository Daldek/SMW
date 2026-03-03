"""Tests for data providers."""

from unittest.mock import MagicMock, patch

import pytest

from providers.parsers import (
    parse_coordinates,
    parse_numeric_value,
    resolve_google_maps_url,
)


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

    def test_parse_coordinates_comma_separator_with_dots(self):
        """Test parsing coordinates with comma separator and dot decimals."""
        lat, lon = parse_coordinates("52.213396, 21.185913")
        assert lat == pytest.approx(52.213396)
        assert lon == pytest.approx(21.185913)

    def test_parse_coordinates_comma_separator_no_space(self):
        """Test parsing coordinates with comma separator without space."""
        lat, lon = parse_coordinates("52.213396,21.185913")
        assert lat == pytest.approx(52.213396)
        assert lon == pytest.approx(21.185913)

    def test_parse_coordinates_with_cardinal_directions(self):
        """Test parsing coordinates with degree symbols and cardinal directions."""
        lat, lon = parse_coordinates("50,33558° N, 19,94761° E")
        assert lat == pytest.approx(50.33558)
        assert lon == pytest.approx(19.94761)


class TestResolveGoogleMapsUrl:
    """Tests for resolve_google_maps_url and Google Maps URL integration."""

    def test_resolve_google_maps_url_search_format(self):
        """Test extracting coordinates from /maps/search/LAT,+LON URL."""
        full_url = "https://www.google.com/maps/search/52.940722,+21.451795?entry=tts"
        mock_resp = MagicMock()
        mock_resp.url = full_url
        mock_resp.close = MagicMock()

        with patch("providers.parsers.urllib.request.build_opener") as mock_opener:
            mock_opener.return_value.open.return_value = mock_resp
            lat, lon = resolve_google_maps_url("https://maps.app.goo.gl/abc123")

        assert lat == pytest.approx(52.940722)
        assert lon == pytest.approx(21.451795)

    def test_resolve_google_maps_url_at_format(self):
        """Test extracting coordinates from /@LAT,LON,17z URL."""
        full_url = "https://www.google.com/maps/@52.2297,21.0122,17z"
        mock_resp = MagicMock()
        mock_resp.url = full_url
        mock_resp.close = MagicMock()

        with patch("providers.parsers.urllib.request.build_opener") as mock_opener:
            mock_opener.return_value.open.return_value = mock_resp
            lat, lon = resolve_google_maps_url("https://maps.app.goo.gl/xyz789")

        assert lat == pytest.approx(52.2297)
        assert lon == pytest.approx(21.0122)

    def test_resolve_google_maps_url_3d4d_format(self):
        """Test extracting coordinates from !3dLAT!4dLON URL."""
        full_url = "https://www.google.com/maps/place/!3d50.33558!4d19.94761"
        mock_resp = MagicMock()
        mock_resp.url = full_url
        mock_resp.close = MagicMock()

        with patch("providers.parsers.urllib.request.build_opener") as mock_opener:
            mock_opener.return_value.open.return_value = mock_resp
            lat, lon = resolve_google_maps_url("https://maps.app.goo.gl/qwe456")

        assert lat == pytest.approx(50.33558)
        assert lon == pytest.approx(19.94761)

    def test_parse_coordinates_google_maps_url(self):
        """Test parse_coordinates delegates to resolve_google_maps_url for Maps URLs."""
        full_url = "https://www.google.com/maps/search/52.940722,+21.451795?entry=tts"
        mock_resp = MagicMock()
        mock_resp.url = full_url
        mock_resp.close = MagicMock()

        with patch("providers.parsers.urllib.request.build_opener") as mock_opener:
            mock_opener.return_value.open.return_value = mock_resp
            lat, lon = parse_coordinates(
                "https://maps.app.goo.gl/aVNcKgJEJkj9fxwS6"
            )

        assert lat == pytest.approx(52.940722)
        assert lon == pytest.approx(21.451795)

    def test_parse_coordinates_google_maps_url_network_error(self):
        """Test parse_coordinates returns (None, None) on network failure."""
        with patch(
            "providers.parsers.urllib.request.build_opener",
            side_effect=OSError("Network unreachable"),
        ):
            lat, lon = parse_coordinates(
                "https://maps.app.goo.gl/aVNcKgJEJkj9fxwS6"
            )

        assert lat is None
        assert lon is None
