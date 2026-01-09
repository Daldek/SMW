# PRD — System wizualizacji danych jakości wód (Web-GUI)

## Cel systemu
System wizualizuje zmienność parametrów fizykochemicznych wód powierzchniowych w przeglądarce, niezależnie od tego, skąd pochodzą dane (Excel, CSV, API w przyszłości). System ujednolica dane do wspólnego modelu domenowego i udostępnia wizualizacje dla użytkowników nietechnicznych i technicznych.

## Problemy użytkowników
- wolontariusze zbierają dane, ale nie umieją ich analizować
- hydrolodzy chcą analizować dane czasowe
- obecnie dane są w Excelu o dynamicznej strukturze
- format danych będzie zmieniał się w przyszłości

## Zakres
- wczytywanie danych przez abstrakcyjnego `DataProvider`
- domain model: measurement points + measurements
- wizualizacja temperatury, pH i tlenu rozpuszczonego
- UI w przeglądarce przez Streamlit
- pełna niezależność wizualizacji od formatu danych źródłowych

## Zakres danych domenowych
W systemie występują dwa stabilne pojęcia:
1. `MeasurementPoint` — punkt poboru
2. `Measurement` — pomiar w czasie

Każdy pomiar zawiera:
- `timestamp`
- `parameters[param_name] = float | None`
- `flags[param_name] = "<" | ">" | None`
- `units[param_name] = string`
- `point_id`
- `metadata`

## Funkcje MVP
**Must Have**
- wczytanie listy punktów z `DataProvider`
- wczytanie pomiarów dla wskazanego punktu z `DataProvider`
- wyświetlanie wykresu z 3 parametrami:
  - temperatura (°C, zakres 0–30)
  - pH (zakres 5–9)
  - tlen (mg/L, zakres 0–15)
- GUI Streamlit:
  - wybór provider’a (na start `ExcelProvider`)
  - wybór pliku
  - wybór punktu

**Nice to Have**
- filtrowanie zakresu dat
- eksport wykresu do PNG

## Użytkownicy
- wolontariusze (głównie wizualizacja)
- hydrolodzy (analiza danych)
- koordynatorzy badań (przegląd wyników)

## Out of Scope
- normy i ocena jakości
- GIS
- PDF raporty
- API / CLI (w przyszłości)

## Wymagania techniczne
- Python 3.12
- pandas (obsługa danych)
- seaborn + matplotlib (wizualizacja)
- Streamlit (web-GUI)
- testy jednostkowe
- Docker-ready

## Kryteria akceptacji
- system uruchamia się przez `streamlit run`
- użytkownik może wybrać plik + punkt
- wyświetla się poprawny wykres
- kod nie posiada zależności od formatu Excela
- testy przechodzą
