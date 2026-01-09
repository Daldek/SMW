"""Visualization utilities for water quality measurement data."""

from typing import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from domain import Measurement


def plot_water_quality(
    measurements: Sequence[Measurement],
    title: str | None = None,
) -> Figure:
    """
    Plot time series of water quality parameters.

    Visualizes temporal variability of:
    - water temperature (°C, range 0-30)
    - pH (range 5-9)
    - dissolved oxygen (mg/L, range 0-15)

    Each parameter is plotted against a separate Y-axis,
    with all axes positioned on the left side.

    Parameters
    ----------
    measurements : Sequence[Measurement]
        Collection of measurements to plot.
    title : str, optional
        Custom title for the plot.

    Returns
    -------
    Figure
        Matplotlib figure object.

    Raises
    ------
    ValueError
        If no measurements are provided.
    """
    if not measurements:
        raise ValueError("No measurements provided for plotting.")

    measurements = sorted(measurements, key=lambda m: m.timestamp)

    dates = []
    temperature = []
    ph_values = []
    oxygen = []

    for m in measurements:
        dates.append(m.timestamp)
        temperature.append(m.parameters.get("water_temperature"))
        ph_values.append(m.parameters.get("pH"))
        oxygen.append(m.parameters.get("dissolved_oxygen"))

    fig, ax_temp = plt.subplots(figsize=(12, 6))
    ax_ph = ax_temp.twinx()
    ax_oxy = ax_temp.twinx()

    # Position all Y-axes on the left side
    ax_ph.spines["left"].set_position(("outward", 60))
    ax_oxy.spines["left"].set_position(("outward", 120))

    ax_ph.spines["right"].set_visible(False)
    ax_oxy.spines["right"].set_visible(False)

    ax_ph.yaxis.set_label_position("left")
    ax_oxy.yaxis.set_label_position("left")

    ax_ph.yaxis.tick_left()
    ax_oxy.yaxis.tick_left()

    # Plot lines
    line_temp, = ax_temp.plot(
        dates,
        temperature,
        color="tab:blue",
        label="Temperatura wody [°C]",
    )

    line_ph, = ax_ph.plot(
        dates,
        ph_values,
        color="tab:orange",
        label="pH",
    )

    line_oxy, = ax_oxy.plot(
        dates,
        oxygen,
        color="darkgreen",
        label="Tlen rozpuszczony [mg/L]",
    )

    # Set labels and ranges
    ax_temp.set_ylabel("Temperatura wody [°C]", color="tab:blue")
    ax_ph.set_ylabel("pH", color="tab:orange")
    ax_oxy.set_ylabel("Tlen rozpuszczony [mg/L]", color="darkgreen")

    ax_temp.set_ylim(0, 30)
    ax_ph.set_ylim(5, 9)
    ax_oxy.set_ylim(0, 15)

    ax_temp.tick_params(axis="y", colors="tab:blue")
    ax_ph.tick_params(axis="y", colors="tab:orange")
    ax_oxy.tick_params(axis="y", colors="darkgreen")

    # Title
    if title:
        fig.suptitle(title, fontsize=14, fontweight="bold")

    # Legend below the plot
    ax_temp.legend(
        handles=[line_temp, line_ph, line_oxy],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=3,
        frameon=False,
    )

    ax_temp.grid(True, linestyle="--", alpha=0.4)
    fig.autofmt_xdate()
    fig.tight_layout()

    return fig
