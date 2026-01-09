"""Parsing utilities for data providers."""

from typing import Optional


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

    text = text.replace(",", ".")
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
