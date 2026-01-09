# Architecture — System wizualizacji danych jakości wód

## Komponenty wysokiego poziomu

System składa się z 4 głównych warstw:

1. **Domain Model**
   - opisuje pojęcia domenowe, np. MeasurementPoint, Measurement
   - niezależny od źródła danych, GUI, wizualizacji

2. **Data Providers (Adapters)**
   - dostarczają dane w formie zgodnej z Domain Model
   - mogą pochodzić z Excela, CSV, API, DB, itp.

3. **Visualization**
   - generuje wykresy na podstawie Domain Model
   - wykorzystuje seaborn + matplotlib
   - nie zna formatu źródłowego danych

4. **GUI (Streamlit)**
   - pozwala użytkownikowi wybierać źródła i punkty
   - prezentuje wykresy
   - nie zawiera logiki domenowej ani logiki parsowania

## Kontrakt domenowy

### `MeasurementPoint`
Minimalny kontrakt:
id: str
metadata: dict[str, Any]

Przykłady `metadata`:
- name
- river
- region
- description

### `Measurement`
Minimalny kontrakt:
point_id: str
timestamp: datetime
parameters: dict[str, float | None]
flags: dict[str, str | None]
units: dict[str, str]
metadata: dict[str, Any]


`parameters` jest dynamiczne → nowe parametry wymagają tylko dodania klucza.

## Provider API

Interfejs:
class DataProvider(Protocol):
def list_points(self) -> list[MeasurementPoint]
def list_measurements(self, point_id: str) -> list[Measurement]

Ważne:
- provider może czytać cokolwiek (Excel, CSV, API)
- musi zwrócić **Domain Model**, a nie DataFrame

## Warstwa Visualization

Wizualizacja nie zna formatu danych, widzi tylko:
list[Measurement]


Parametry wykresu:
- seaborn lineplot
- 3 osie Y po lewej
- zakresy:
  - temperatura: 0–30°C
  - pH: 5–9
  - tlen: 0–15 mg/L

## Warstwa GUI

GUI wykonuje:
1. wybór provider'a (np. `ExcelProvider`)
2. wybór pliku (`file_uploader`)
3. wybór punktu (`selectbox`)
4. render wykresu (`st.pyplot`)

GUI **nie zna**:
- pandas,
- Excela,
- skiprows,
- kolumn,
- parserów.

## Testy

Testowane są:
- provider (parsowanie źródeł)
- domain model (integralność)
- visualization (brak błędów przy renderowaniu)
- wartości `<` `>` w parach (value, flag)

## Rozszerzalność

Dodanie nowego źródła danych = dodanie adaptera zgodnego z `DataProvider`.

Przykłady potencjalnych providerów:
- `ExcelProvider(path)`
- `CSVProvider(path)`
- `APIProvider(url)`
- `MockProvider()` (do testów)

Provider'y nie wpływają na kod GUI lub visualization.

## Zależności

- Python 3.12
- pandas (przetwarzanie danych tabelarycznych)
- seaborn (rysowanie, style)
- matplotlib (backend + osi)
- streamlit (web GUI)
