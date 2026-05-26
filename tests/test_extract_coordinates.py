"""Testy skryptu scripts/extract_coordinates.py."""

import tempfile
from pathlib import Path

import pytest
from openpyxl import Workbook

from scripts.extract_coordinates import (
    collect_coordinates,
    iter_xlsx_files,
    main,
    write_output,
)


POINTS_HEADER = [
    "Nazwa punktu",
    "Kod punktu",
    "Współrzędne punktu",
    "Nazwa rzeki",
    "Kod JCWP",
    "Zarząd zlewni",
    "RZGW",
    "Opis lokalizacji",
    "Otoczenie",
    "Osoba badająca",
    "Kontakt",
]


def _make_workbook(rows: list[list]) -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = "Punkty"
    ws.append(POINTS_HEADER)
    for row in rows:
        ws.append(row)
    return wb


def _save(wb: Workbook, directory: Path, name: str) -> Path:
    path = directory / name
    wb.save(path)
    return path


@pytest.fixture()
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


class TestIterXlsxFiles:
    def test_finds_xlsx_recursively(self, tmp_dir):
        (tmp_dir / "sub").mkdir()
        wb = _make_workbook([])
        wb.save(tmp_dir / "a.xlsx")
        wb.save(tmp_dir / "sub" / "b.xlsx")

        result = iter_xlsx_files(tmp_dir)
        names = [p.name for p in result]
        assert names == ["a.xlsx", "b.xlsx"]

    def test_skips_excel_lock_files(self, tmp_dir):
        wb = _make_workbook([])
        wb.save(tmp_dir / "a.xlsx")
        wb.save(tmp_dir / "~$a.xlsx")

        result = iter_xlsx_files(tmp_dir)
        assert [p.name for p in result] == ["a.xlsx"]


class TestCollectCoordinates:
    def test_extracts_coordinates_in_wgs84(self, tmp_dir):
        wb = _make_workbook(
            [["Punkt A", "P001", "50.123456 19.654321", "", "", "", "", "", "", "", ""]]
        )
        _save(wb, tmp_dir, "file.xlsx")

        coords = collect_coordinates(tmp_dir)

        assert coords == {"P001": (50.123456, 19.654321)}

    def test_skips_points_without_coordinates(self, tmp_dir, capsys):
        wb = _make_workbook(
            [
                ["Punkt A", "P001", "50.1 19.6", "", "", "", "", "", "", "", ""],
                ["Punkt B", "P002", "", "", "", "", "", "", "", "", ""],
            ]
        )
        _save(wb, tmp_dir, "file.xlsx")

        coords = collect_coordinates(tmp_dir)
        captured = capsys.readouterr()

        assert list(coords.keys()) == ["P001"]
        assert "P002" in captured.err
        assert "brak współrzędnych" in captured.err

    def test_dedupe_by_point_id_first_wins(self, tmp_dir):
        wb1 = _make_workbook(
            [["Punkt A", "P001", "50.1 19.6", "", "", "", "", "", "", "", ""]]
        )
        wb2 = _make_workbook(
            [["Punkt A", "P001", "51.0 20.0", "", "", "", "", "", "", "", ""]]
        )
        _save(wb1, tmp_dir, "a.xlsx")
        _save(wb2, tmp_dir, "b.xlsx")

        coords = collect_coordinates(tmp_dir)

        assert coords == {"P001": (50.1, 19.6)}

    def test_skips_invalid_files(self, tmp_dir, capsys):
        broken = Workbook()
        broken.active.title = "NiePunkty"
        broken.save(tmp_dir / "broken.xlsx")

        wb_ok = _make_workbook(
            [["Punkt A", "P001", "50.1 19.6", "", "", "", "", "", "", "", ""]]
        )
        _save(wb_ok, tmp_dir, "ok.xlsx")

        coords = collect_coordinates(tmp_dir)
        captured = capsys.readouterr()

        assert list(coords.keys()) == ["P001"]
        assert "broken.xlsx" in captured.err


class TestWriteOutput:
    def test_writes_sorted_semicolon_separated(self, tmp_dir):
        output = tmp_dir / "out.txt"
        coords = {
            "P002": (52.229676, 21.012229),
            "P001": (50.123456, 19.654321),
        }

        write_output(coords, output)

        text = output.read_text(encoding="utf-8")
        assert text == (
            "lat,lon\n"
            "50.123456,19.654321\n"
            "52.229676,21.012229\n"
        )

    def test_empty_input_writes_header_only(self, tmp_dir):
        output = tmp_dir / "out.txt"
        write_output({}, output)

        assert output.exists()
        assert output.read_text(encoding="utf-8") == "lat,lon\n"

    def test_creates_parent_directory(self, tmp_dir):
        output = tmp_dir / "nested" / "deep" / "out.txt"
        write_output({"P001": (50.0, 20.0)}, output)

        assert output.exists()


class TestMain:
    def test_end_to_end(self, tmp_dir, capsys):
        wb = _make_workbook(
            [["Punkt A", "P001", "50.1 19.6", "", "", "", "", "", "", "", ""]]
        )
        _save(wb, tmp_dir, "file.xlsx")
        output = tmp_dir / "out.txt"

        exit_code = main([str(tmp_dir), str(output)])

        assert exit_code == 0
        assert output.read_text(encoding="utf-8") == (
            "lat,lon\n50.100000,19.600000\n"
        )

    def test_missing_directory_returns_error(self, tmp_dir, capsys):
        output = tmp_dir / "out.txt"

        exit_code = main([str(tmp_dir / "missing"), str(output)])
        captured = capsys.readouterr()

        assert exit_code == 2
        assert "nie istnieje" in captured.err
