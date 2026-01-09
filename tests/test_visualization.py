"""Tests for visualization module."""

from datetime import datetime

import pytest
from matplotlib.figure import Figure

from domain import Measurement
from visualization import plot_water_quality


class TestPlotWaterQuality:
    """Tests for plot_water_quality function."""

    def test_plot_creates_figure(self):
        """Test that plot_water_quality returns a Figure."""
        measurements = [
            Measurement(
                point_id="P001",
                timestamp=datetime(2024, 1, 15, 10, 0),
                parameters={
                    "water_temperature": 10.0,
                    "pH": 7.0,
                    "dissolved_oxygen": 9.0,
                },
            ),
            Measurement(
                point_id="P001",
                timestamp=datetime(2024, 2, 15, 10, 0),
                parameters={
                    "water_temperature": 12.0,
                    "pH": 7.2,
                    "dissolved_oxygen": 8.5,
                },
            ),
        ]

        fig = plot_water_quality(measurements)

        assert isinstance(fig, Figure)

    def test_plot_with_title(self):
        """Test that plot_water_quality accepts custom title."""
        measurements = [
            Measurement(
                point_id="P001",
                timestamp=datetime(2024, 1, 15, 10, 0),
                parameters={"water_temperature": 10.0},
            ),
        ]

        fig = plot_water_quality(measurements, title="Test Title")

        assert isinstance(fig, Figure)
        assert fig._suptitle.get_text() == "Test Title"

    def test_plot_raises_on_empty_list(self):
        """Test that plot_water_quality raises on empty list."""
        with pytest.raises(ValueError, match="No measurements provided"):
            plot_water_quality([])

    def test_plot_with_missing_parameters(self):
        """Test plotting with some missing parameters."""
        measurements = [
            Measurement(
                point_id="P001",
                timestamp=datetime(2024, 1, 15, 10, 0),
                parameters={"water_temperature": 10.0},
            ),
            Measurement(
                point_id="P001",
                timestamp=datetime(2024, 2, 15, 10, 0),
                parameters={"pH": 7.2},
            ),
        ]

        fig = plot_water_quality(measurements)

        assert isinstance(fig, Figure)

    def test_plot_sorts_by_timestamp(self):
        """Test that measurements are sorted by timestamp."""
        measurements = [
            Measurement(
                point_id="P001",
                timestamp=datetime(2024, 3, 15, 10, 0),
                parameters={"water_temperature": 15.0},
            ),
            Measurement(
                point_id="P001",
                timestamp=datetime(2024, 1, 15, 10, 0),
                parameters={"water_temperature": 10.0},
            ),
            Measurement(
                point_id="P001",
                timestamp=datetime(2024, 2, 15, 10, 0),
                parameters={"water_temperature": 12.0},
            ),
        ]

        fig = plot_water_quality(measurements)

        assert isinstance(fig, Figure)
