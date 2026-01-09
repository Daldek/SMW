"""Visualization utilities for water quality measurement data."""

from typing import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from domain import Measurement


def _has_valid_data(values: list) -> bool:
    """Check if list contains any non-None values."""
    return any(v is not None for v in values)


def _extract_param_data(
    measurements: Sequence[Measurement],
    param_name: str,
) -> tuple[list, list, list, list, list]:
    """
    Extract parameter data separating flagged and non-flagged values.

    Returns
    -------
    tuple
        (all_dates, all_values, flagged_dates, flagged_values, has_flags)
    """
    all_dates = []
    all_values = []
    flagged_dates = []
    flagged_values = []

    for m in measurements:
        value = m.parameters.get(param_name)
        all_dates.append(m.timestamp)
        all_values.append(value)

        flag = m.flags.get(param_name)
        if flag in ("<", ">") and value is not None:
            flagged_dates.append(m.timestamp)
            flagged_values.append(value)

    has_flags = len(flagged_values) > 0
    return all_dates, all_values, flagged_dates, flagged_values, has_flags


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
    - conductivity (µS/cm, range 0-3500)

    Values with '<' or '>' flags are marked with black-edged markers.

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

    # Extract data for each parameter
    params_config = {
        "water_temperature": {"color": "tab:blue", "label": "Temperatura wody [°C]"},
        "pH": {"color": "tab:orange", "label": "pH"},
        "dissolved_oxygen": {"color": "darkgreen", "label": "Tlen rozpuszczony [mg/L]"},
        "conductivity": {"color": "tab:purple", "label": "Przewodność [µS/cm]"},
    }

    param_data = {}
    any_flags = False
    for param in params_config:
        data = _extract_param_data(measurements, param)
        param_data[param] = data
        if data[4]:  # has_flags
            any_flags = True

    fig, ax_temp = plt.subplots(figsize=(14, 6))
    ax_ph = ax_temp.twinx()
    ax_oxy = ax_temp.twinx()
    ax_cond = ax_temp.twinx()

    axes = {
        "water_temperature": ax_temp,
        "pH": ax_ph,
        "dissolved_oxygen": ax_oxy,
        "conductivity": ax_cond,
    }

    limits = {
        "water_temperature": (0, 30),
        "pH": (5, 9),
        "dissolved_oxygen": (0, 15),
        "conductivity": (0, 3500),
    }

    # Position all Y-axes on the left side
    ax_ph.spines["left"].set_position(("outward", 60))
    ax_oxy.spines["left"].set_position(("outward", 120))
    ax_cond.spines["left"].set_position(("outward", 180))

    ax_ph.spines["right"].set_visible(False)
    ax_oxy.spines["right"].set_visible(False)
    ax_cond.spines["right"].set_visible(False)

    ax_ph.yaxis.set_label_position("left")
    ax_oxy.yaxis.set_label_position("left")
    ax_cond.yaxis.set_label_position("left")

    ax_ph.yaxis.tick_left()
    ax_oxy.yaxis.tick_left()
    ax_cond.yaxis.tick_left()

    handles = []

    # Plot lines and flagged markers
    for param, config in params_config.items():
        dates, values, flag_dates, flag_values, has_flags = param_data[param]
        ax = axes[param]

        if _has_valid_data(values):
            line, = ax.plot(
                dates,
                values,
                color=config["color"],
                label=config["label"],
            )
            handles.append(line)
            ax.set_ylabel(config["label"], color=config["color"])
            ax.tick_params(axis="y", colors=config["color"])

            # Mark flagged values with black-edged markers
            if has_flags:
                ax.scatter(
                    flag_dates,
                    flag_values,
                    color=config["color"],
                    edgecolors="black",
                    linewidths=1.5,
                    s=60,
                    zorder=5,
                )

        ax.set_ylim(limits[param])

    # Title
    if title:
        fig.suptitle(title, fontsize=14, fontweight="bold")

    # Legend below the plot
    if handles:
        ax_temp.legend(
            handles=handles,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.15),
            ncol=len(handles),
            frameon=False,
        )

    ax_temp.grid(True, linestyle="--", alpha=0.4)
    fig.autofmt_xdate()
    fig.tight_layout()

    # Add note about flagged values (after tight_layout)
    if any_flags:
        fig.text(
            0.5, 0.02,
            "* Punkty z czarną obwódką oznaczają wartości z flagą '<' lub '>' (poza zakresem pomiaru)",
            ha="center",
            fontsize=9,
            style="italic",
            transform=fig.transFigure,
        )
        fig.subplots_adjust(bottom=0.18)

    return fig


def plot_chemical_parameters(
    measurements: Sequence[Measurement],
    title: str | None = None,
) -> Figure:
    """
    Plot scatter chart of chemical parameters.

    Visualizes:
    - nitrates (azotany) [mg/L]
    - nitrites (azotyny) [mg/L]
    - phosphates (fosforany) [mg/L]
    - chlorides (chlorki) [mg/L]
    - sulphates (siarczany) [mg/L]

    Only parameters with data are shown in the legend.
    Values with '<' or '>' flags are marked with black-edged markers.

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

    param_config = {
        "nitrates": {"label": "Azotany [mg/L]", "color": "tab:blue", "marker": "o"},
        "nitrites": {"label": "Azotyny [mg/L]", "color": "tab:orange", "marker": "s"},
        "phosphates": {"label": "Fosforany [mg/L]", "color": "tab:green", "marker": "^"},
        "chlorides": {"label": "Chlorki [mg/L]", "color": "tab:red", "marker": "d"},
        "sulphates": {"label": "Siarczany [mg/L]", "color": "tab:purple", "marker": "v"},
    }

    # Extract data with flag information
    param_data = {}
    any_flags = False
    for param in param_config:
        data = _extract_param_data(measurements, param)
        param_data[param] = data
        if data[4]:  # has_flags
            any_flags = True

    fig, ax = plt.subplots(figsize=(14, 6))
    handles = []

    for param, config in param_config.items():
        dates, values, flag_dates, flag_values, has_flags = param_data[param]

        if _has_valid_data(values):
            # Separate flagged and non-flagged points
            normal_dates = []
            normal_values = []
            for i, (d, v) in enumerate(zip(dates, values)):
                if v is not None and d not in flag_dates:
                    normal_dates.append(d)
                    normal_values.append(v)

            # Plot non-flagged points
            scatter = ax.scatter(
                normal_dates,
                normal_values,
                c=config["color"],
                marker=config["marker"],
                label=config["label"],
                s=50,
                alpha=0.7,
            )
            handles.append(scatter)

            # Plot flagged points with black edge
            if has_flags:
                ax.scatter(
                    flag_dates,
                    flag_values,
                    c=config["color"],
                    marker=config["marker"],
                    s=70,
                    alpha=0.9,
                    edgecolors="black",
                    linewidths=1.5,
                    zorder=5,
                )

    ax.set_ylabel("Stężenie [mg/L]")
    ax.set_xlabel("Data")

    if title:
        fig.suptitle(title, fontsize=14, fontweight="bold")

    if handles:
        ax.legend(
            handles=handles,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.15),
            ncol=len(handles),
            frameon=False,
        )

    ax.grid(True, linestyle="--", alpha=0.4)
    fig.autofmt_xdate()
    fig.tight_layout()

    # Add note about flagged values (after tight_layout)
    if any_flags:
        fig.text(
            0.5, 0.02,
            "* Punkty z czarną obwódką oznaczają wartości z flagą '<' lub '>' (poza zakresem pomiaru)",
            ha="center",
            fontsize=9,
            style="italic",
            transform=fig.transFigure,
        )
        fig.subplots_adjust(bottom=0.18)

    return fig
