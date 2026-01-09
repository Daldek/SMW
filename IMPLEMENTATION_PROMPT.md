# Implementation Prompt — dla Claude Code

Wygeneruj kompletny projekt Python zgodny z poniższymi wymaganiami:

## Wymagania ogólne
- Python 3.12
- Moduły:
  - `domain`
  - `providers`
  - `visualization`
  - `gui`
  - `tests`

## Domain Model
Stwórz klasy:

class MeasurementPoint:
id: str
metadata: dict[str, Any]

class Measurement:
point_id: str
timestamp: datetime
parameters: dict[str, float | None]
flags: dict[str, str | None]
units: dict[str, str]
metadata: dict[str, Any]

## Data Providers
Stwórz interfejs:
class DataProvider(Protocol):
def list_points(self) -> list[MeasurementPoint]
def list_measurements(self, point_id: str) -> list[Measurement]


Stwórz implementację `ExcelProvider` działającą na pandas.

## Visualization
Utwórz funkcję:
def plot_water_quality(measurements: list[Measurement]) -> matplotlib.figure.Figure


Wymagania:
- seaborn + matplotlib
- 3 parametry:
  - `water_temperature` (°C)
  - `pH`
  - `dissolved_oxygen` (mg/L)
- 3 osie Y po lewej
- zakresy:
  - temp: 0–30
  - pH: 5–9
  - tlen: 0–15

## GUI
Stwórz Streamlit UI (`gui/app.py`), który:
- umożliwia upload pliku Excel
- instancjonuje `ExcelProvider`
- wyświetla listę punktów (selectbox)
- wyświetla wykres (`st.pyplot`)

## Testy
Stwórz testy dla:
- parsowania wartości `<` `>`
- listowania punktów
- listowania pomiarów
- wizualizacji bez błędów

## Dodatkowe wymagania
- użyj: `pandas`, `seaborn`, `matplotlib`, `streamlit`
- kod w stylu `numpy_docstring`
- zgodność z PEP8

Zastosuj wszystkie reguły z RULES.md oraz założenia z PRD.md i ARCHITECTURE.md