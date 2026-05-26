"""
Skan katalogu plików `.xlsx` i eksport współrzędnych punktów do pliku `.csv`.

Skrypt przeznaczony do uruchamiania jako zadanie CRON. Skanuje wskazany
katalog (rekurencyjnie) w poszukiwaniu plików `.xlsx` zgodnych ze
strukturą `ExcelProvider`, zbiera współrzędne punktów pomiarowych w
WGS84 i zapisuje je do pliku tekstowego w formacie:

    lat,lon
    50.123456,19.654321
    ...

Pierwszy wiersz to nagłówek z nazwami kolumn. Separator: przecinek.
Separator dziesiętny: kropka. Współrzędne z 6 miejscami po przecinku.
Deduplikacja punktów po `point_id` odbywa się wewnętrznie — sam
identyfikator nie trafia do pliku wyjściowego.
Punkty bez współrzędnych są pomijane, a informacja o nich trafia do
stderr.

Uruchomienie
------------
    python -m scripts.extract_coordinates <katalog_xlsx> <plik_wyjsciowy.csv>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from providers.excel import ExcelProvider
from providers.exceptions import InvalidFileStructureError

COORD_PRECISION = 6
FIELD_SEPARATOR = ","
HEADER = ("lat", "lon")


def iter_xlsx_files(directory: Path) -> list[Path]:
    """Zwróć posortowaną listę plików .xlsx w katalogu (rekurencyjnie)."""
    files = [p for p in directory.rglob("*.xlsx") if not p.name.startswith("~$")]
    return sorted(files)


def collect_coordinates(directory: Path) -> dict[str, tuple[float, float]]:
    """
    Zbierz unikalne współrzędne punktów ze wszystkich plików .xlsx.

    Deduplikacja po `point_id` — pierwsze wystąpienie wygrywa.
    Punkty bez współrzędnych są pomijane i logowane do stderr.
    """
    coords: dict[str, tuple[float, float]] = {}
    files = iter_xlsx_files(directory)

    if not files:
        print(f"Brak plików .xlsx w katalogu: {directory}", file=sys.stderr)
        return coords

    for xlsx in files:
        try:
            provider = ExcelProvider(str(xlsx))
            points = provider.list_points()
        except InvalidFileStructureError as exc:
            print(f"[SKIP] {xlsx.name}: {exc}", file=sys.stderr)
            continue
        except Exception as exc:
            print(f"[ERROR] {xlsx.name}: {exc}", file=sys.stderr)
            continue

        for point in points:
            lat = point.metadata.get("latitude")
            lon = point.metadata.get("longitude")

            if lat is None or lon is None:
                print(
                    f"[SKIP] {xlsx.name} :: {point.id}: brak współrzędnych",
                    file=sys.stderr,
                )
                continue

            if point.id in coords:
                continue

            coords[point.id] = (lat, lon)

    return coords


def write_output(coords: dict[str, tuple[float, float]], output_path: Path) -> None:
    """Zapisz współrzędne do pliku tekstowego, posortowane po point_id."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [FIELD_SEPARATOR.join(HEADER)]
    lines.extend(
        FIELD_SEPARATOR.join(
            [
                f"{lat:.{COORD_PRECISION}f}",
                f"{lon:.{COORD_PRECISION}f}",
            ]
        )
        for _, (lat, lon) in sorted(coords.items())
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Skanuje katalog .xlsx i eksportuje współrzędne punktów (WGS84) "
            "do pliku tekstowego. Format wiersza: point_id,lat,lon"
        )
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Katalog z plikami .xlsx (skanowany rekurencyjnie).",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Plik wyjściowy .csv.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.directory.is_dir():
        print(
            f"Katalog nie istnieje lub nie jest katalogiem: {args.directory}",
            file=sys.stderr,
        )
        return 2

    coords = collect_coordinates(args.directory)
    write_output(coords, args.output)

    print(
        f"Zapisano {len(coords)} punktów do {args.output}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
