"""Domain model for water quality monitoring system."""

from domain.measurement import Measurement
from domain.point import MeasurementPoint

__all__ = ["Measurement", "MeasurementPoint"]
