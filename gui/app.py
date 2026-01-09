"""Streamlit GUI for water quality visualization."""

import io
import tempfile
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from providers import ExcelProvider
from visualization import plot_chemical_parameters, plot_water_quality


def render_single_file_mode() -> None:
    """Render single file upload and visualization mode."""
    uploaded_file = st.file_uploader(
        "Wybierz plik Excel z danymi pomiarowymi",
        type=["xlsx", "xls"],
    )

    if uploaded_file is None:
        st.info("Zaladuj plik Excel, aby rozpoczac.")
        return

    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(uploaded_file.name).suffix
    ) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        provider = ExcelProvider(tmp_path)
        points = provider.list_points()

        if not points:
            st.warning("Nie znaleziono punktow pomiarowych w pliku.")
            return

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
            st.warning("Brak pomiarow dla wybranego punktu.")
            return

        st.success(f"Zaladowano {len(measurements)} pomiarow.")

        point = next(p for p in points if p.id == point_id)

        st.subheader("Parametry fizykochemiczne")
        title1 = f"Zmiennosc parametrow fizykochemicznych - {point.name}"
        fig1 = plot_water_quality(measurements, title=title1)
        st.pyplot(fig1)

        st.subheader("Zwiazki chemiczne")
        title2 = f"Stezenia zwiazkow chemicznych - {point.name}"
        fig2 = plot_chemical_parameters(measurements, title=title2)
        st.pyplot(fig2)

    except Exception as e:
        st.error(f"Blad podczas przetwarzania pliku: {e}")

    finally:
        Path(tmp_path).unlink(missing_ok=True)


def render_batch_mode() -> None:
    """Render batch processing mode for generating plots from uploaded files."""
    st.markdown(
        "Zaladuj pliki Excel i wygeneruj wykresy dla wszystkich punktow pomiarowych. "
        "Wyniki zostana spakowane do pliku ZIP do pobrania."
    )

    uploaded_files = st.file_uploader(
        "Wybierz pliki Excel",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
    )

    if not uploaded_files:
        st.info("Zaladuj pliki Excel, aby wygenerowac wykresy.")
        return

    # Filter out temp files
    valid_files = [f for f in uploaded_files if not f.name.startswith("~$")]

    if not valid_files:
        st.warning("Nie znaleziono prawidlowych plikow Excel.")
        return

    # Limit number of files
    MAX_FILES = 20
    if len(valid_files) > MAX_FILES:
        st.error(f"Maksymalnie mozna przeslac {MAX_FILES} plikow naraz.")
        return

    st.info(f"Zaladowano {len(valid_files)} plikow Excel.")

    if st.button("Generuj wykresy", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        total_plots = 0
        errors = []

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for i, uploaded_file in enumerate(valid_files):
                status_text.text(f"Przetwarzanie: {uploaded_file.name}")

                # Save uploaded file to temp location
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=Path(uploaded_file.name).suffix
                ) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                try:
                    provider = ExcelProvider(tmp_path)
                    points = provider.list_points()

                    for point in points:
                        measurements = provider.list_measurements(point.id)

                        if not measurements:
                            continue

                        # Sanitize point name for filename
                        safe_name = "".join(
                            c if c.isalnum() or c in (" ", "-", "_") else "_"
                            for c in point.name
                        ).strip()

                        # Generate physicochemical plot
                        title1 = f"Zmiennosc parametrow fizykochemicznych - {point.name}"
                        fig1 = plot_water_quality(measurements, title=title1)

                        img_buffer1 = io.BytesIO()
                        fig1.savefig(img_buffer1, format="png", dpi=150, bbox_inches="tight")
                        img_buffer1.seek(0)
                        zip_file.writestr(f"{safe_name}_fizykochemiczne.png", img_buffer1.read())
                        plt.close(fig1)
                        total_plots += 1

                        # Generate chemical plot
                        title2 = f"Stezenia zwiazkow chemicznych - {point.name}"
                        fig2 = plot_chemical_parameters(measurements, title=title2)

                        img_buffer2 = io.BytesIO()
                        fig2.savefig(img_buffer2, format="png", dpi=150, bbox_inches="tight")
                        img_buffer2.seek(0)
                        zip_file.writestr(f"{safe_name}_chemiczne.png", img_buffer2.read())
                        plt.close(fig2)
                        total_plots += 1

                except Exception as e:
                    errors.append(f"{uploaded_file.name}: {e}")

                finally:
                    Path(tmp_path).unlink(missing_ok=True)

                progress_bar.progress((i + 1) / len(valid_files))

        status_text.empty()
        progress_bar.empty()

        if total_plots > 0:
            st.success(f"Wygenerowano {total_plots} wykresow.")

            zip_buffer.seek(0)
            st.download_button(
                label="Pobierz wykresy (ZIP)",
                data=zip_buffer,
                file_name="wykresy.zip",
                mime="application/zip",
                type="primary",
            )

        if errors:
            with st.expander(f"Bledy ({len(errors)})"):
                for error in errors:
                    st.error(error)


def main() -> None:
    """
    Main entry point for the Streamlit application.

    Provides a web interface for uploading Excel files with water quality
    measurements, selecting measurement points, and displaying interactive
    plots of physicochemical parameters.

    The application supports two modes:
    1. Single file - upload and visualize one file at a time
    2. Batch mode - generate plots for all Excel files in a folder
    """
    st.set_page_config(
        page_title="Wizualizacja jakosci wod",
        page_icon="💧",
        layout="wide",
    )

    st.title("System wizualizacji parametrow jakosci wod")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Pojedynczy plik", "Generowanie z folderu"])

    with tab1:
        render_single_file_mode()

    with tab2:
        render_batch_mode()


if __name__ == "__main__":
    main()
