"""Streamlit GUI for water quality visualization."""

import tempfile
from pathlib import Path

import streamlit as st

from providers import ExcelProvider
from visualization import plot_water_quality


def main() -> None:
    """
    Main entry point for the Streamlit application.

    Provides a web interface for uploading Excel files with water quality
    measurements, selecting measurement points, and displaying interactive
    plots of physicochemical parameters.

    The application workflow:
    1. User uploads an Excel file
    2. User selects a measurement point from available options
    3. Application displays a plot with temperature, pH, and dissolved oxygen
    """
    st.set_page_config(
        page_title="Wizualizacja jakości wód",
        page_icon="💧",
        layout="wide",
    )

    st.title("System wizualizacji parametrów jakości wód")
    st.markdown("---")

    # File upload
    uploaded_file = st.file_uploader(
        "Wybierz plik Excel z danymi pomiarowymi",
        type=["xlsx", "xls"],
    )

    if uploaded_file is None:
        st.info("Załaduj plik Excel, aby rozpocząć.")
        return

    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(uploaded_file.name).suffix
    ) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        provider = ExcelProvider(tmp_path)
        points = provider.list_points()

        if not points:
            st.warning("Nie znaleziono punktów pomiarowych w pliku.")
            return

        # Point selection
        point_options = {f"{p.name} ({p.id})": p.id for p in points}
        selected_label = st.selectbox(
            "Wybierz punkt pomiarowy",
            options=list(point_options.keys()),
        )

        if selected_label is None:
            return

        point_id = point_options[selected_label]
        measurements = provider.list_measurements(point_id)

        if not measurements:
            st.warning("Brak pomiarów dla wybranego punktu.")
            return

        st.success(f"Załadowano {len(measurements)} pomiarów.")

        # Get point metadata for title
        point = next(p for p in points if p.id == point_id)
        title = f"Zmienność parametrów fizykochemicznych – {point.name}"

        # Display plot
        fig = plot_water_quality(measurements, title=title)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Błąd podczas przetwarzania pliku: {e}")

    finally:
        # Cleanup temporary file
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
