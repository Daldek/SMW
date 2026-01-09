"""Excel data provider for water quality measurements."""

from datetime import datetime, time, date
from typing import Any

import pandas as pd

from domain import Measurement, MeasurementPoint
from providers.parsers import parse_coordinates, parse_numeric_value


class ExcelProvider:
    """
    Data provider for Excel files with water quality measurements.

    The Excel file must contain a sheet named 'Punkty' describing
    all measurement points. Each measurement point must have
    a corresponding sheet with the same name containing measurement data.

    Parameters
    ----------
    path : str
        Path to the Excel file.
    """

    POINTS_SHEET = "Punkty"
    MEASUREMENTS_START_ROW = 8

    # Column names in 'Punkty' sheet
    COL_CODE = "Kod punktu"
    COL_COORDS = "Współrzędne punktu"
    COL_RIVER = "Nazwa rzeki"
    COL_JCWP = "Kod JCWP"
    COL_CATCHMENT = "Zarząd zlewni"
    COL_RZGW = "RZGW"
    COL_NAME = "Nazwa punktu"
    COL_LOCATION = "Opis lokalizacji"
    COL_SURROUNDINGS = "Otoczenie"
    COL_INVESTIGATOR = "Osoba badająca"
    COL_CONTACT = "Kontakt"

    # Parameter definitions with units
    PARAMETERS = {
        "water_temperature": {"index": 11, "unit": "°C"},
        "transparency": {"index": 12, "unit": "cm"},
        "dissolved_oxygen": {"index": 13, "unit": "mg/L"},
        "nitrates": {"index": 16, "unit": "mg/L"},
        "nitrites": {"index": 17, "unit": "mg/L"},
        "phosphates": {"index": 18, "unit": "mg/L"},
        "chlorides": {"index": 19, "unit": "mg/L"},
        "sulphates": {"index": 20, "unit": "mg/L"},
        "pH": {"index": 21, "unit": ""},
        "water_temperature_home": {"index": 22, "unit": "°C"},
        "conductivity": {"index": 23, "unit": "µS/cm"},
    }

    def __init__(self, path: str) -> None:
        """
        Initialize the Excel provider.

        Parameters
        ----------
        path : str
            Path to the Excel file.
        """
        self._path = path
        self._points: dict[str, MeasurementPoint] | None = None

    def list_points(self) -> list[MeasurementPoint]:
        """
        List all measurement points from the Excel file.

        Returns
        -------
        list[MeasurementPoint]
            List of measurement points.
        """
        if self._points is None:
            self._load_points()
        return list(self._points.values())

    def list_measurements(self, point_id: str) -> list[Measurement]:
        """
        List all measurements for a given point.

        Parameters
        ----------
        point_id : str
            Identifier of the measurement point.

        Returns
        -------
        list[Measurement]
            List of measurements for the specified point.
        """
        if self._points is None:
            self._load_points()

        point = self._points.get(point_id)
        if point is None:
            return []

        return self._load_measurements(point)

    def _load_points(self) -> None:
        """Load measurement points from the Excel file."""
        df = pd.read_excel(self._path, sheet_name=self.POINTS_SHEET)
        self._points = {}

        for _, row in df.iterrows():
            lat, lon = parse_coordinates(row[self.COL_COORDS])

            name = str(row[self.COL_NAME]).strip()
            code = row[self.COL_CODE]
            point_id = name if pd.isna(code) else str(code).strip()

            point = MeasurementPoint(
                id=point_id,
                name=name,
                metadata={
                    "river_name": str(row[self.COL_RIVER]).strip(),
                    "jcwp_code": str(row[self.COL_JCWP]).strip(),
                    "catchment_authority": str(row[self.COL_CATCHMENT]).strip(),
                    "rzgw": str(row[self.COL_RZGW]).strip(),
                    "location_description": str(row[self.COL_LOCATION]).strip(),
                    "surroundings": str(row[self.COL_SURROUNDINGS]).strip(),
                    "investigator": str(row[self.COL_INVESTIGATOR]).strip(),
                    "contact": str(row[self.COL_CONTACT]).strip(),
                    "latitude": lat,
                    "longitude": lon,
                },
            )

            self._points[point.id] = point

    def _load_measurements(self, point: MeasurementPoint) -> list[Measurement]:
        """Load measurements for a specific point."""
        df = pd.read_excel(
            self._path,
            sheet_name=point.name,
            header=None,
            skiprows=self.MEASUREMENTS_START_ROW,
        )

        measurements: list[Measurement] = []

        for _, row in df.iterrows():
            if pd.isna(row.iloc[0]):
                continue

            measurement = self._parse_measurement_row(row, point.id)
            if measurement is not None:
                measurements.append(measurement)

        return measurements

    def _parse_measurement_row(
        self, row: pd.Series, point_id: str
    ) -> Measurement | None:
        """Parse a single Excel row into a Measurement object."""
        sample_date = self._parse_date(row.iloc[0])
        if sample_date is None:
            return None

        sample_time = self._parse_time(row.iloc[1])

        timestamp = datetime.combine(
            sample_date, sample_time or datetime.min.time()
        )

        metadata = self._extract_metadata(row)
        parameters, flags, units = self._extract_parameters(row)

        return Measurement(
            point_id=point_id,
            timestamp=timestamp,
            parameters=parameters,
            flags=flags,
            units=units,
            metadata=metadata,
        )

    def _extract_metadata(self, row: pd.Series) -> dict[str, Any]:
        """Extract metadata from a measurement row."""
        return {
            "sampling_location": row.iloc[2],
            "depth_info": row.iloc[3],
            "sample_volume_l": row.iloc[4],
            "water_state": row.iloc[5],
            "water_gauge_state": row.iloc[6],
            "precipitation_mm": row.iloc[7],
            "precipitation_description": row.iloc[8],
            "anomalies": row.iloc[9],
            "field_test_time": row.iloc[10],
            "home_test_date": row.iloc[14],
            "home_test_time": row.iloc[15],
            "calibration_date": row.iloc[24],
            "remarks": row.iloc[25],
        }

    def _extract_parameters(
        self, row: pd.Series
    ) -> tuple[dict[str, float | None], dict[str, str | None], dict[str, str]]:
        """Extract numeric parameters, flags, and units from a row."""
        parameters: dict[str, float | None] = {}
        flags: dict[str, str | None] = {}
        units: dict[str, str] = {}

        for name, config in self.PARAMETERS.items():
            value, flag = parse_numeric_value(row.iloc[config["index"]])
            if value is not None:
                parameters[name] = value
                units[name] = config["unit"]
            if flag is not None:
                flags[name] = flag

        return parameters, flags, units

    @staticmethod
    def _parse_date(value) -> date | None:
        """Parse date from Excel cell."""
        try:
            return pd.to_datetime(value).date()
        except Exception:
            return None

    @staticmethod
    def _parse_time(value) -> time | None:
        """Parse time from Excel cell."""
        if value is None or pd.isna(value):
            return None

        if isinstance(value, time):
            return value

        if isinstance(value, pd.Timestamp):
            return value.time()

        if isinstance(value, (float, int)):
            try:
                return (
                    pd.Timestamp("1899-12-30") + pd.to_timedelta(value, unit="D")
                ).time()
            except Exception:
                return None

        try:
            return pd.to_datetime(value).time()
        except Exception:
            return None
