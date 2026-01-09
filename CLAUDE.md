# Claude.md

## Nazwa projektu
System wizualizacji parametrów jakości wód w web-GUI

## Cel projektu
Zapewnienie przeglądarkowego narzędzia do wizualizacji danych pomiarowych jakości wód na podstawie różnych źródeł danych wejściowych, z zachowaniem niezależności warstw (provider → domain → visualization → GUI).

## Kluczowe założenia
- Python 3.12
- GUI w Streamlit (web)
- Dane wejściowe w przyszłości zmienne (Excel, CSV, API itp.)
- Warstwa wizualizacji **nie zależy od formatu źródła danych**
- Warstwa analityczna **nie zna szczegółów importu**
- `DataProvider` jest jedynym punktem wejścia dla danych
- Domain Model jest stabilny i niezależny od źródeł danych
- Pełne testy jednostkowe (dla providerów, modeli, wizualizacji)
- Obsługa flag pomiarowych `<` i `>`
- Obsługa jednostek parametrów

## Dokumenty projektu
W repo znajdują się cztery główne pliki specyfikacji:

- `PRD.md` — opis produktu i wymagań funkcjonalnych
- `ARCHITECTURE.md` — szczegóły architektury i modułów
- `IMPLEMENTATION_PROMPT.md` — instrukcje implementacyjne dla LLM
- `RULES.md` — reguły techniczne i standardy

Podczas generowania kodu Claude powinien stosować się do wszystkich powyższych plików.

## Architektura (skrót)

### Warstwy systemu
1. **Domain Model**
   - `MeasurementPoint`
   - `Measurement`
   Domain Model jest niezależny od źródła danych i GUI.

2. **Data Providers**
   - adaptery wczytujące i mapujące źródła do Domain Model
   - przykłady:
     - `ExcelProvider`
     - `CSVProvider`
     - `APIProvider`
     - `MockProvider`
   - provider implementuje kontrakt:
     ```
     list_points() -> list[MeasurementPoint]
     list_measurements(point_id: str) -> list[Measurement]
     ```

3. **Visualization**
   - generuje wykresy na podstawie `list[Measurement]`
   - używa seaborn + matplotlib
   - nie zależy od providerów ani Streamlit

4. **GUI**
   - Streamlit
   - wybór danych, punktu, parametrów
   - wywołuje provider + visualization
   - nie zawiera logiki domenowej ani parsowania

## Domain Model

### `Measurement`
Zawiera:
- `point_id: str`
- `timestamp: datetime`
- `parameters: dict[str, float | None]` (dynamiczne)
- `flags: dict[str, str | None]` (`"<"`, `">"` lub `None`)
- `units: dict[str, str]`
- `metadata: dict[str, Any]`

### `MeasurementPoint`
Zawiera:
- `id: str`
- `metadata: dict[str, Any]`

## Wymagania wizualizacji (MVP)
Parametry obowiązkowe:
- temperatura (°C)
- pH
- tlen rozpuszczony (mg/L)

Format wykresu:
- 3 osie Y po lewej stronie
- zakresy:
  - temperatura: `0–30°C`
  - pH: `5–9`
  - tlen: `0–15 mg/L`
- legenda pod wykresem
- seaborn + matplotlib

## Zakres GUI (MVP)
- upload pliku wejściowego
- wybór punktu z listy
- wyświetlenie wykresu

## Testy
Wymagane testy obejmują:
- provider: parsowanie danych, wartości `<`, `>`
- domain: integralność struktur
- visualization: bezbłędne renderowanie figur
- brak testów dla UI w MVP

## Wymagania techniczne
- Python 3.12
- pandas (tylko w providerach)
- seaborn (wizualizacja)
- matplotlib (backend)
- streamlit (GUI)
- numpy_docstring (dokumentacja)
- zgodność z PEP8

## Stan projektu
Specyfikacja jest kompletna. Implementacja ma być zgodna z:
- `PRD.md`
- `ARCHITECTURE.md`
- `IMPLEMENTATION_PROMPT.md`
- `RULES.md`
