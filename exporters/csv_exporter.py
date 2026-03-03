"""CSV exporter for water quality measurement data."""

import csv
import io
from datetime import datetime

from domain import Measurement, MeasurementPoint

# Parameters in export column order (matching ExcelProvider.PARAMETERS)
EXPORT_PARAMETERS = [
    "water_temperature",
    "transparency",
    "dissolved_oxygen",
    "nitrates",
    "nitrites",
    "phosphates",
    "chlorides",
    "sulphates",
    "pH",
    "water_temperature_home",
    "conductivity",
]

CSV_COLUMNS = [
    "point_id",
    "point_name",
    "river_name",
    "jcwp_code",
    "catchment_authority",
    "rzgw",
    "latitude",
    "longitude",
    "timestamp",
    *EXPORT_PARAMETERS,
]

ERROR_CSV_COLUMNS = ["filename", "error_type", "error_message"]

# UTF-8 BOM for Excel compatibility
UTF8_BOM = "\ufeff"


def format_parameter_value(value: float | None, flag: str | None) -> str:
    """
    Format a parameter value with its flag for CSV output.

    Parameters
    ----------
    value : float or None
        Numeric parameter value.
    flag : str or None
        Range qualifier ('<' or '>'), or None.

    Returns
    -------
    str
        Formatted value string (e.g. '<0.05', '7.2', '').
    """
    if value is None:
        return ""
    formatted = f"{value:g}"
    if flag:
        return f"{flag}{formatted}"
    return formatted


def get_latest_measurement(
    measurements: list[Measurement],
) -> Measurement | None:
    """
    Return the measurement with the most recent timestamp.

    Parameters
    ----------
    measurements : list[Measurement]
        List of measurements for a single point.

    Returns
    -------
    Measurement or None
        The most recent measurement, or None if the list is empty.
    """
    if not measurements:
        return None
    return max(measurements, key=lambda m: m.timestamp)


def build_export_row(
    point: MeasurementPoint, measurement: Measurement
) -> dict[str, str]:
    """
    Build a single CSV row dict from a point and its measurement.

    Parameters
    ----------
    point : MeasurementPoint
        The measurement point.
    measurement : Measurement
        A measurement taken at the point.

    Returns
    -------
    dict[str, str]
        Dictionary keyed by CSV_COLUMNS with string values.
    """
    meta = point.metadata
    row: dict[str, str] = {
        "point_id": point.id,
        "point_name": point.name,
        "river_name": str(meta.get("river_name", "") or ""),
        "jcwp_code": str(meta.get("jcwp_code", "") or ""),
        "catchment_authority": str(meta.get("catchment_authority", "") or ""),
        "rzgw": str(meta.get("rzgw", "") or ""),
        "latitude": str(meta.get("latitude", "")) if meta.get("latitude") is not None else "",
        "longitude": str(meta.get("longitude", "")) if meta.get("longitude") is not None else "",
        "timestamp": measurement.timestamp.strftime("%Y-%m-%d %H:%M"),
    }

    for param in EXPORT_PARAMETERS:
        value = measurement.parameters.get(param)
        flag = measurement.flags.get(param)
        row[param] = format_parameter_value(value, flag)

    return row


def export_csv(
    points: list[MeasurementPoint],
    measurements_by_point: dict[str, list[Measurement]],
) -> str:
    """
    Generate a full CSV string from points and their measurements.

    Uses the latest measurement for each point.

    Parameters
    ----------
    points : list[MeasurementPoint]
        List of measurement points.
    measurements_by_point : dict[str, list[Measurement]]
        Mapping from point_id to list of measurements.

    Returns
    -------
    str
        Complete CSV content with UTF-8 BOM.
    """
    rows: list[dict[str, str]] = []

    for point in points:
        point_measurements = measurements_by_point.get(point.id, [])
        latest = get_latest_measurement(point_measurements)
        if latest is None:
            continue
        rows.append(build_export_row(point, latest))

    return write_csv(rows)


def merge_csv(existing_content: str, new_rows: list[dict[str, str]]) -> str:
    """
    Merge new rows into an existing CSV, updating by point_id.

    Existing rows with matching point_id are replaced.
    New rows with unknown point_id are appended.
    Existing rows without a match are preserved.

    Parameters
    ----------
    existing_content : str
        Content of the existing CSV file.
    new_rows : list[dict[str, str]]
        New rows to merge (as dicts keyed by CSV_COLUMNS).

    Returns
    -------
    str
        Merged CSV content with UTF-8 BOM.
    """
    # Strip BOM if present
    content = existing_content.lstrip(UTF8_BOM)

    reader = csv.DictReader(io.StringIO(content))
    existing_rows: dict[str, dict[str, str]] = {}
    for row in reader:
        pid = row.get("point_id", "")
        if pid:
            existing_rows[pid] = row

    # Apply new rows (update or add)
    new_by_id: dict[str, dict[str, str]] = {}
    for row in new_rows:
        pid = row.get("point_id", "")
        if pid:
            new_by_id[pid] = row

    for pid, row in new_by_id.items():
        existing_rows[pid] = row

    return write_csv(list(existing_rows.values()))


def build_error_csv(
    errors: list[dict[str, str]],
) -> str:
    """
    Generate a CSV string with processing errors.

    Parameters
    ----------
    errors : list[dict[str, str]]
        List of error dicts with keys: filename, error_type, error_message.

    Returns
    -------
    str
        CSV content with UTF-8 BOM.
    """
    output = io.StringIO()
    output.write(UTF8_BOM)
    writer = csv.DictWriter(
        output, fieldnames=ERROR_CSV_COLUMNS, lineterminator="\n"
    )
    writer.writeheader()
    for error in errors:
        writer.writerow(error)
    return output.getvalue()


def write_csv(rows: list[dict[str, str]]) -> str:
    """
    Write rows to a CSV string with BOM and header.

    Parameters
    ----------
    rows : list[dict[str, str]]
        Row dicts keyed by CSV_COLUMNS.

    Returns
    -------
    str
        CSV content with UTF-8 BOM.
    """
    output = io.StringIO()
    output.write(UTF8_BOM)
    writer = csv.DictWriter(
        output, fieldnames=CSV_COLUMNS, lineterminator="\n"
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return output.getvalue()
