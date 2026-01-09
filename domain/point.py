"""Domain model for measurement points."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MeasurementPoint:
    """
    Measurement point representing a fixed spatial location.

    Parameters
    ----------
    id : str
        Unique identifier of the measurement point.
    name : str
        Human-readable name of the measurement point.
    metadata : dict[str, Any]
        Additional descriptive information (river name, coordinates, etc.).
    """

    id: str
    name: str
    metadata: dict[str, Any] = field(default_factory=dict)
