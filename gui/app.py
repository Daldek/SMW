"""Streamlit GUI for water quality visualization."""

import io
import tempfile
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from exporters import (
    build_error_csv,
    build_export_row,
    export_csv,
    get_latest_measurement,
    merge_csv,
    write_csv,
)
from providers import ExcelProvider
from providers.exceptions import InvalidFileStructureError
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

        # --- CSV Export ---
        st.markdown("---")
        st.subheader("Eksport CSV")

        measurements_by_point: dict[str, list] = {}
        for p in points:
            p_measurements = provider.list_measurements(p.id)
            if p_measurements:
                measurements_by_point[p.id] = p_measurements

        existing_csv = st.file_uploader(
            "Istniejacy plik CSV do aktualizacji (opcjonalnie)",
            type=["csv"],
            key="csv_upload",
        )

        if existing_csv is not None:
            new_rows = []
            for p in points:
                p_measurements = measurements_by_point.get(p.id, [])
                latest = get_latest_measurement(p_measurements)
                if latest:
                    new_rows.append(build_export_row(p, latest))

            csv_content = merge_csv(
                existing_csv.getvalue().decode("utf-8-sig"), new_rows
            )
        else:
            csv_content = export_csv(points, measurements_by_point)

        st.download_button(
            label="Pobierz wyniki (CSV)",
            data=csv_content.encode("utf-8-sig"),
            file_name="wyniki.csv",
            mime="text/csv",
        )

    except InvalidFileStructureError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Nieoczekiwany blad: {e}")

    finally:
        Path(tmp_path).unlink(missing_ok=True)


def _pick_folder() -> None:
    """Open a native folder picker dialog and store the result in session state."""
    import subprocess
    import sys

    if sys.platform == "darwin":
        script = (
            'tell application "System Events" to activate\n'
            'set theFolder to choose folder with prompt "Wybierz folder z plikami Excel"\n'
            'return POSIX path of theFolder'
        )
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=60,
        )
        folder = result.stdout.strip()
    else:
        return

    if folder:
        st.session_state.batch_folder = folder


def _clean_path(raw: str) -> str:
    """Strip surrounding quotes and whitespace from a pasted path."""
    cleaned = raw.strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in ("'", '"'):
        cleaned = cleaned[1:-1]
    return cleaned


def render_batch_mode() -> None:
    """Render batch processing mode for generating plots from a folder."""
    st.markdown(
        "Podaj sciezke do folderu z plikami Excel. "
        "Wykresy zostana wygenerowane dla wszystkich punktow pomiarowych "
        "i spakowane do pliku ZIP do pobrania."
    )

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        raw_path = st.text_input(
            "Sciezka do folderu z plikami Excel",
            key="batch_folder",
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Wybierz folder", on_click=_pick_folder)

    folder_path = _clean_path(raw_path) if raw_path else ""

    if not folder_path:
        st.info("Podaj sciezke do folderu, aby wygenerowac wykresy.")
        return

    folder = Path(folder_path)

    if not folder.is_dir():
        st.error(f"Podana sciezka nie jest folderem: {folder_path}")
        return

    # Find Excel files, skip temp files
    excel_files = sorted(
        p for p in folder.iterdir()
        if p.suffix.lower() in (".xlsx", ".xls") and not p.name.startswith("~$")
    )

    if not excel_files:
        st.warning("Nie znaleziono plikow Excel w podanym folderze.")
        return

    st.info(f"Znaleziono {len(excel_files)} plikow Excel.")

    # Clear cached results when folder changes
    if st.session_state.get("_batch_folder_prev") != folder_path:
        for key in ("batch_zip", "batch_csv", "batch_error_csv",
                     "batch_total_plots", "batch_errors"):
            st.session_state.pop(key, None)
        st.session_state["_batch_folder_prev"] = folder_path

    if st.button("Generuj wykresy", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        total_plots = 0
        errors = []
        all_export_rows: list[dict[str, str]] = []
        csv_errors: list[dict[str, str]] = []

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for i, excel_path in enumerate(excel_files):
                status_text.text(f"Przetwarzanie: {excel_path.name}")

                try:
                    file_prefix = excel_path.stem
                    provider = ExcelProvider(str(excel_path))
                    points = provider.list_points()

                    for point in points:
                        measurements = provider.list_measurements(point.id)

                        if not measurements:
                            continue

                        # Collect CSV export row
                        latest = get_latest_measurement(measurements)
                        if latest:
                            all_export_rows.append(
                                build_export_row(point, latest)
                            )

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
                        zip_file.writestr(f"{file_prefix}_{safe_name}_fizykochemiczne.png", img_buffer1.read())
                        plt.close(fig1)
                        total_plots += 1

                        # Generate chemical plot
                        title2 = f"Stezenia zwiazkow chemicznych - {point.name}"
                        fig2 = plot_chemical_parameters(measurements, title=title2)

                        img_buffer2 = io.BytesIO()
                        fig2.savefig(img_buffer2, format="png", dpi=150, bbox_inches="tight")
                        img_buffer2.seek(0)
                        zip_file.writestr(f"{file_prefix}_{safe_name}_chemiczne.png", img_buffer2.read())
                        plt.close(fig2)
                        total_plots += 1

                except Exception as e:
                    errors.append(f"{excel_path.name}: {e}")
                    csv_errors.append({
                        "filename": excel_path.name,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    })

                progress_bar.progress((i + 1) / len(excel_files))

        status_text.empty()
        progress_bar.empty()

        # Deduplicate CSV rows by point_id (keep latest timestamp)
        unique_rows: dict[str, dict[str, str]] = {}
        for row in all_export_rows:
            pid = row["point_id"]
            if pid not in unique_rows or row["timestamp"] > unique_rows[pid]["timestamp"]:
                unique_rows[pid] = row

        # Store results in session state so they survive reruns
        zip_buffer.seek(0)
        st.session_state["batch_zip"] = zip_buffer.getvalue()
        st.session_state["batch_total_plots"] = total_plots
        st.session_state["batch_errors"] = errors
        if unique_rows:
            st.session_state["batch_csv"] = write_csv(
                list(unique_rows.values())
            ).encode("utf-8-sig")
        else:
            st.session_state.pop("batch_csv", None)
        if csv_errors:
            st.session_state["batch_error_csv"] = build_error_csv(
                csv_errors
            ).encode("utf-8-sig")
        else:
            st.session_state.pop("batch_error_csv", None)

    # --- Display results from session state ---
    if "batch_total_plots" not in st.session_state:
        return

    total_plots = st.session_state["batch_total_plots"]
    if total_plots > 0:
        st.success(f"Wygenerowano {total_plots} wykresow.")
        st.download_button(
            label="Pobierz wykresy (ZIP)",
            data=st.session_state["batch_zip"],
            file_name="wykresy.zip",
            mime="application/zip",
            type="primary",
        )

    if st.session_state.get("batch_csv"):
        st.download_button(
            label="Pobierz wyniki (CSV)",
            data=st.session_state["batch_csv"],
            file_name="wyniki.csv",
            mime="text/csv",
        )

    if st.session_state.get("batch_error_csv"):
        st.download_button(
            label="Pobierz bledy (CSV)",
            data=st.session_state["batch_error_csv"],
            file_name="error_wyniki.csv",
            mime="text/csv",
        )

    errors = st.session_state.get("batch_errors", [])
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

    tab1, tab2 = st.tabs(["Pojedynczy plik", "Generowanie z folderu (batch)"])

    with tab1:
        render_single_file_mode()

    with tab2:
        render_batch_mode()


if __name__ == "__main__":
    main()
