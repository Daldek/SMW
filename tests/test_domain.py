"""Tests for domain model."""

from datetime import datetime

import pytest

from domain import Measurement, MeasurementPoint


class TestMeasurementPoint:
    """Tests for MeasurementPoint class."""

    def test_create_measurement_point(self):
        """Test creating a measurement point with minimal data."""
        point = MeasurementPoint(id="P001", name="Test Point")

        assert point.id == "P001"
        assert point.name == "Test Point"
        assert point.metadata == {}

    def test_create_measurement_point_with_metadata(self):
        """Test creating a measurement point with metadata."""
        metadata = {
            "river_name": "Wisła",
            "latitude": 52.2297,
            "longitude": 21.0122,
        }
        point = MeasurementPoint(id="P001", name="Test Point", metadata=metadata)

        assert point.metadata["river_name"] == "Wisła"
        assert point.metadata["latitude"] == 52.2297

    def test_measurement_point_is_frozen(self):
        """Test that MeasurementPoint is immutable."""
        point = MeasurementPoint(id="P001", name="Test Point")

        with pytest.raises(Exception):
            point.id = "P002"


class TestMeasurement:
    """Tests for Measurement class."""

    def test_create_measurement(self):
        """Test creating a measurement with minimal data."""
        measurement = Measurement(
            point_id="P001",
            timestamp=datetime(2024, 1, 15, 10, 30),
        )

        assert measurement.point_id == "P001"
        assert measurement.timestamp == datetime(2024, 1, 15, 10, 30)
        assert measurement.parameters == {}
        assert measurement.flags == {}
        assert measurement.units == {}
        assert measurement.metadata == {}

    def test_create_measurement_with_parameters(self):
        """Test creating a measurement with parameters."""
        measurement = Measurement(
            point_id="P001",
            timestamp=datetime(2024, 1, 15, 10, 30),
            parameters={
                "water_temperature": 15.5,
                "pH": 7.2,
                "dissolved_oxygen": 8.5,
            },
            flags={"nitrates": "<"},
            units={
                "water_temperature": "°C",
                "pH": "",
                "dissolved_oxygen": "mg/L",
            },
        )

        assert measurement.parameters["water_temperature"] == 15.5
        assert measurement.parameters["pH"] == 7.2
        assert measurement.flags["nitrates"] == "<"
        assert measurement.units["water_temperature"] == "°C"

    def test_measurement_parameter_with_none_value(self):
        """Test that parameters can have None values."""
        measurement = Measurement(
            point_id="P001",
            timestamp=datetime(2024, 1, 15, 10, 30),
            parameters={
                "water_temperature": 15.5,
                "pH": None,
            },
        )

        assert measurement.parameters["water_temperature"] == 15.5
        assert measurement.parameters["pH"] is None
