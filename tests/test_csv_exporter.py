"""Tests for CSV exporter module."""

from datetime import datetime

from domain import Measurement, MeasurementPoint
from exporters.csv_exporter import (
    CSV_COLUMNS,
    UTF8_BOM,
    build_error_csv,
    build_export_row,
    export_csv,
    format_parameter_value,
    get_latest_measurement,
    merge_csv,
)


class TestFormatParameterValue:
    """Tests for format_parameter_value."""

    def test_none_value(self):
        assert format_parameter_value(None, None) == ""

    def test_none_value_with_flag(self):
        assert format_parameter_value(None, "<") == ""

    def test_plain_value(self):
        assert format_parameter_value(7.2, None) == "7.2"

    def test_integer_value(self):
        assert format_parameter_value(10.0, None) == "10"

    def test_less_than_flag(self):
        assert format_parameter_value(0.05, "<") == "<0.05"

    def test_greater_than_flag(self):
        assert format_parameter_value(100.0, ">") == ">100"

    def test_zero_value(self):
        assert format_parameter_value(0.0, None) == "0"


class TestGetLatestMeasurement:
    """Tests for get_latest_measurement."""

    def test_empty_list(self):
        assert get_latest_measurement([]) is None

    def test_single_measurement(self):
        m = Measurement(
            point_id="P1", timestamp=datetime(2024, 1, 1, 10, 0)
        )
        assert get_latest_measurement([m]) is m

    def test_multiple_measurements(self):
        m1 = Measurement(
            point_id="P1", timestamp=datetime(2024, 1, 1, 10, 0)
        )
        m2 = Measurement(
            point_id="P1", timestamp=datetime(2024, 6, 15, 12, 0)
        )
        m3 = Measurement(
            point_id="P1", timestamp=datetime(2024, 3, 1, 8, 0)
        )
        assert get_latest_measurement([m1, m2, m3]) is m2


class TestBuildExportRow:
    """Tests for build_export_row."""

    def test_complete_row(self):
        point = MeasurementPoint(
            id="P1",
            name="Punkt 1",
            metadata={
                "latitude": 52.1234,
                "longitude": 21.0567,
                "river_name": "Wisla",
                "jcwp_code": "RW200001",
                "catchment_authority": "ZZ w Warszawie",
                "rzgw": "RZGW w Warszawie",
            },
        )
        measurement = Measurement(
            point_id="P1",
            timestamp=datetime(2024, 6, 15, 10, 30),
            parameters={"water_temperature": 18.5, "pH": 7.2},
            flags={"water_temperature": None, "pH": None},
            units={"water_temperature": "°C", "pH": ""},
        )
        row = build_export_row(point, measurement)

        assert row["point_id"] == "P1"
        assert row["point_name"] == "Punkt 1"
        assert row["river_name"] == "Wisla"
        assert row["jcwp_code"] == "RW200001"
        assert row["catchment_authority"] == "ZZ w Warszawie"
        assert row["rzgw"] == "RZGW w Warszawie"
        assert row["latitude"] == "52.1234"
        assert row["longitude"] == "21.0567"
        assert row["timestamp"] == "2024-06-15 10:30"
        assert row["water_temperature"] == "18.5"
        assert row["pH"] == "7.2"
        assert row["dissolved_oxygen"] == ""

    def test_row_with_flags(self):
        point = MeasurementPoint(
            id="P1", name="Punkt 1", metadata={}
        )
        measurement = Measurement(
            point_id="P1",
            timestamp=datetime(2024, 1, 1),
            parameters={"nitrites": 0.05, "phosphates": 0.01},
            flags={"nitrites": "<", "phosphates": "<"},
        )
        row = build_export_row(point, measurement)

        assert row["nitrites"] == "<0.05"
        assert row["phosphates"] == "<0.01"

    def test_missing_coordinates(self):
        point = MeasurementPoint(
            id="P1", name="Punkt 1", metadata={}
        )
        measurement = Measurement(
            point_id="P1", timestamp=datetime(2024, 1, 1)
        )
        row = build_export_row(point, measurement)

        assert row["latitude"] == ""
        assert row["longitude"] == ""

    def test_none_coordinates(self):
        point = MeasurementPoint(
            id="P1",
            name="Punkt 1",
            metadata={"latitude": None, "longitude": None},
        )
        measurement = Measurement(
            point_id="P1", timestamp=datetime(2024, 1, 1)
        )
        row = build_export_row(point, measurement)

        assert row["latitude"] == ""
        assert row["longitude"] == ""


class TestExportCsv:
    """Tests for export_csv."""

    def test_single_point(self):
        point = MeasurementPoint(
            id="P1",
            name="Punkt 1",
            metadata={"latitude": 52.0, "longitude": 21.0},
        )
        m = Measurement(
            point_id="P1",
            timestamp=datetime(2024, 6, 15, 10, 0),
            parameters={"pH": 7.0},
        )
        result = export_csv([point], {"P1": [m]})

        assert result.startswith(UTF8_BOM)
        lines = result.strip().split("\n")
        assert len(lines) == 2  # header + 1 data row
        assert "point_id" in lines[0]
        assert "P1" in lines[1]

    def test_multiple_points(self):
        p1 = MeasurementPoint(id="P1", name="Punkt 1", metadata={})
        p2 = MeasurementPoint(id="P2", name="Punkt 2", metadata={})
        m1 = Measurement(
            point_id="P1", timestamp=datetime(2024, 1, 1)
        )
        m2 = Measurement(
            point_id="P2", timestamp=datetime(2024, 2, 1)
        )
        result = export_csv([p1, p2], {"P1": [m1], "P2": [m2]})

        lines = result.strip().split("\n")
        assert len(lines) == 3  # header + 2 data rows

    def test_skips_points_without_measurements(self):
        p1 = MeasurementPoint(id="P1", name="Punkt 1", metadata={})
        p2 = MeasurementPoint(id="P2", name="Punkt 2", metadata={})
        m1 = Measurement(
            point_id="P1", timestamp=datetime(2024, 1, 1)
        )
        result = export_csv([p1, p2], {"P1": [m1]})

        lines = result.strip().split("\n")
        assert len(lines) == 2  # header + 1 data row

    def test_uses_latest_measurement(self):
        point = MeasurementPoint(id="P1", name="Punkt 1", metadata={})
        m_old = Measurement(
            point_id="P1",
            timestamp=datetime(2024, 1, 1),
            parameters={"pH": 6.0},
        )
        m_new = Measurement(
            point_id="P1",
            timestamp=datetime(2024, 6, 1),
            parameters={"pH": 7.5},
        )
        result = export_csv([point], {"P1": [m_old, m_new]})

        assert "7.5" in result
        assert "6" not in result.split("\n")[-1]

    def test_csv_has_all_columns(self):
        point = MeasurementPoint(id="P1", name="Punkt 1", metadata={})
        m = Measurement(
            point_id="P1", timestamp=datetime(2024, 1, 1)
        )
        result = export_csv([point], {"P1": [m]})

        header = result.lstrip(UTF8_BOM).split("\n")[0]
        for col in CSV_COLUMNS:
            assert col in header


class TestMergeCsv:
    """Tests for merge_csv."""

    def _make_csv(self, rows_data):
        """Helper to build CSV content for testing."""
        import csv
        import io

        output = io.StringIO()
        output.write(UTF8_BOM)
        writer = csv.DictWriter(
            output, fieldnames=CSV_COLUMNS, lineterminator="\n"
        )
        writer.writeheader()
        for row in rows_data:
            full_row = {col: "" for col in CSV_COLUMNS}
            full_row.update(row)
            writer.writerow(full_row)
        return output.getvalue()

    def test_update_existing_row(self):
        existing = self._make_csv(
            [{"point_id": "P1", "point_name": "Old Name", "pH": "6.5"}]
        )
        new_rows = [
            {col: "" for col in CSV_COLUMNS}
            | {"point_id": "P1", "point_name": "New Name", "pH": "7.0"}
        ]
        result = merge_csv(existing, new_rows)

        assert "New Name" in result
        assert "Old Name" not in result

    def test_preserve_unchanged_rows(self):
        existing = self._make_csv(
            [
                {"point_id": "P1", "point_name": "Punkt 1"},
                {"point_id": "P2", "point_name": "Punkt 2"},
            ]
        )
        new_rows = [
            {col: "" for col in CSV_COLUMNS}
            | {"point_id": "P1", "point_name": "Updated Punkt 1"}
        ]
        result = merge_csv(existing, new_rows)

        lines = result.strip().split("\n")
        assert len(lines) == 3  # header + 2 rows
        assert "Punkt 2" in result
        assert "Updated Punkt 1" in result

    def test_add_new_rows(self):
        existing = self._make_csv(
            [{"point_id": "P1", "point_name": "Punkt 1"}]
        )
        new_rows = [
            {col: "" for col in CSV_COLUMNS}
            | {"point_id": "P3", "point_name": "Punkt 3"}
        ]
        result = merge_csv(existing, new_rows)

        lines = result.strip().split("\n")
        assert len(lines) == 3  # header + 2 rows
        assert "Punkt 1" in result
        assert "Punkt 3" in result

    def test_result_has_bom(self):
        existing = self._make_csv([{"point_id": "P1"}])
        result = merge_csv(existing, [])

        assert result.startswith(UTF8_BOM)


class TestBuildErrorCsv:
    """Tests for build_error_csv."""

    def test_single_error(self):
        errors = [
            {
                "filename": "test.xlsx",
                "error_type": "InvalidFileStructureError",
                "error_message": "Brak arkusza",
            }
        ]
        result = build_error_csv(errors)

        assert result.startswith(UTF8_BOM)
        lines = result.strip().split("\n")
        assert len(lines) == 2
        assert "filename" in lines[0]
        assert "test.xlsx" in lines[1]

    def test_multiple_errors(self):
        errors = [
            {
                "filename": "a.xlsx",
                "error_type": "Error",
                "error_message": "msg1",
            },
            {
                "filename": "b.xlsx",
                "error_type": "Error",
                "error_message": "msg2",
            },
        ]
        result = build_error_csv(errors)

        lines = result.strip().split("\n")
        assert len(lines) == 3

    def test_empty_errors(self):
        result = build_error_csv([])

        lines = result.strip().split("\n")
        assert len(lines) == 1  # header only
        assert "filename" in lines[0]
