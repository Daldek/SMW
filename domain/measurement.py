"""Domain model for water quality measurements."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Measurement:
    """
    Single physicochemical water measurement.

    One instance corresponds to one sampling event.

    Parameters
    ----------
    point_id : str
        Identifier of the measurement point.
    timestamp : datetime
        Date and time of sample collection.
    parameters : dict[str, float | None]
        Numeric physicochemical parameters (e.g., temperature, pH).
    flags : dict[str, str | None]
        Flags for values outside measurement range ('<', '>').
    units : dict[str, str]
        Units for each parameter (e.g., '°C', 'mg/L').
    metadata : dict[str, Any]
        Additional contextual information.
    """

    point_id: str
    timestamp: datetime
    parameters: dict[str, float | None] = field(default_factory=dict)
    flags: dict[str, str | None] = field(default_factory=dict)
    units: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
