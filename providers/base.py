"""Base protocol for data providers."""

from typing import Protocol

from domain import Measurement, MeasurementPoint


class DataProvider(Protocol):
    """
    Protocol defining the interface for data providers.

    All data providers must implement this interface to ensure
    consistent access to measurement data regardless of the source.
    """

    def list_points(self) -> list[MeasurementPoint]:
        """
        List all available measurement points.

        Returns
        -------
        list[MeasurementPoint]
            List of measurement points available in the data source.
        """
        ...

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
        ...
