"""Parsing utilities for data providers."""

import logging
import re
import urllib.request
from typing import Optional

logger = logging.getLogger(__name__)

_GOOGLE_MAPS_HOSTS = ("maps.app.goo.gl", "goo.gl/maps", "google.com/maps")


def _is_google_maps_url(text: str) -> bool:
    """Check if text is a Google Maps URL."""
    return text.startswith("http") and any(h in text for h in _GOOGLE_MAPS_HOSTS)


def resolve_google_maps_url(url: str) -> tuple[Optional[float], Optional[float]]:
    """
    Resolve a Google Maps URL and extract coordinates.

    Handles shortened URLs (maps.app.goo.gl) by following the redirect,
    then extracts lat/lon from the full URL.

    Parameters
    ----------
    url : str
        Google Maps URL (shortened or full).

    Returns
    -------
    tuple[float | None, float | None]
        Latitude and longitude, or (None, None) on failure.
    """
    try:
        full_url = _resolve_redirect(url)
    except Exception:
        logger.warning("Failed to resolve Google Maps URL: %s", url)
        return None, None

    return _extract_coords_from_url(full_url)


def _resolve_redirect(url: str) -> str:
    """Follow a single redirect and return the Location header, or the original URL."""
    req = urllib.request.Request(url, method="HEAD")
    # Don't follow redirects automatically — read Location header
    opener = urllib.request.build_opener(urllib.request.HTTPHandler)
    resp = opener.open(req, timeout=5)
    final_url = resp.url  # urllib follows redirects; use the final URL
    resp.close()
    return final_url


def _extract_coords_from_url(url: str) -> tuple[Optional[float], Optional[float]]:
    """
    Extract coordinates from a full Google Maps URL.

    Supported patterns:
    - /maps/search/LAT,+LON or /maps/search/LAT,LON
    - /@LAT,LON,
    - !3dLAT!4dLON
    """
    patterns = [
        r"/maps/search/([-\d.]+),\+?([-\d.]+)",
        r"/@([-\d.]+),([-\d.]+),",
        r"!3d([-\d.]+)!4d([-\d.]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            try:
                return float(match.group(1)), float(match.group(2))
            except ValueError:
                continue
    return None, None


def parse_numeric_value(value) -> tuple[Optional[float], Optional[str]]:
    """
    Parse numeric value with optional range qualifier.

    Supports values like:
    - 1.23
    - "<0.05"
    - ">100"

    Parameters
    ----------
    value : any
        Raw value from data source.

    Returns
    -------
    tuple[float | None, str | None]
        Parsed numeric value and flag ('<', '>' or None).
    """
    if value is None:
        return None, None

    if isinstance(value, (int, float)):
        return float(value), None

    if not isinstance(value, str):
        return None, None

    text = value.strip()
    if not text:
        return None, None

    flag = None
    if text.startswith("<"):
        flag = "<"
        text = text[1:]
    elif text.startswith(">"):
        flag = ">"
        text = text[1:]

    try:
        return float(text.replace(",", ".")), flag
    except ValueError:
        return None, None


def parse_coordinates(value: str) -> tuple[Optional[float], Optional[float]]:
    """
    Parse geographic coordinates from a text field.

    Supports formats like:
    - "52.1234 21.0123"
    - "52,1234 21,0123"
    - "52,1234;21,0123"

    Parameters
    ----------
    value : str
        Raw coordinate string.

    Returns
    -------
    tuple[float | None, float | None]
        Latitude and longitude in decimal degrees.
    """
    if not isinstance(value, str):
        return None, None

    text = value.strip()
    if not text:
        return None, None

    if _is_google_maps_url(text):
        return resolve_google_maps_url(text)

    # Handle format with cardinal directions (e.g. "50,33558° N, 19,94761° E")

    dms_match = re.match(
        r"([\d,\.]+)\s*°?\s*[NS]\s*,\s*([\d,\.]+)\s*°?\s*[EW]", text
    )
    if dms_match:
        try:
            lat = float(dms_match.group(1).replace(",", "."))
            lon = float(dms_match.group(2).replace(",", "."))
            return lat, lon
        except ValueError:
            pass

    # Try comma as value separator first (e.g. "52.213396, 21.185913")
    if "," in text:
        parts = [p.strip() for p in text.split(",")]
        if len(parts) == 2:
            try:
                return (
                    float(parts[0].replace(",", ".")),
                    float(parts[1].replace(",", ".")),
                )
            except ValueError:
                pass
        # Comma may be a decimal separator (e.g. "52,1234 21,0123")
        text = text.replace(",", ".")

    # Try semicolon as value separator (e.g. "52,1234;21,0123")
    text = text.replace(";", " ")

    parts = text.split()
    if len(parts) != 2:
        return None, None

    try:
        lat = float(parts[0])
        lon = float(parts[1])
    except ValueError:
        return None, None

    return lat, lon
