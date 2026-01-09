# System Wizualizacji Parametrów Jakości Wód

Przeglądarkowe narzędzie do wizualizacji danych pomiarowych jakości wód powierzchniowych.

## Opis

System umożliwia wizualizację zmienności parametrów fizykochemicznych wód na podstawie danych z różnych źródeł (Excel, CSV, API). Architektura oparta na warstwach zapewnia niezależność wizualizacji od formatu danych źródłowych.

### Główne funkcje

- Wczytywanie danych z plików Excel
- Wybór punktu pomiarowego
- Wizualizacja trzech parametrów na jednym wykresie:
  - Temperatura wody (0-30°C)
  - pH (5-9)
  - Tlen rozpuszczony (0-15 mg/L)

## Wymagania

- Python 3.12+

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone <url-repozytorium>
cd SMW
```

2. Utwórz i aktywuj środowisko wirtualne:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# lub
.venv\Scripts\activate     # Windows
```

3. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

## Uruchomienie

```bash
streamlit run gui/app.py
```

Aplikacja otworzy się w przeglądarce pod adresem `http://localhost:8501`.

## Użytkowanie

1. Załaduj plik Excel z danymi pomiarowymi
2. Wybierz punkt pomiarowy z listy
3. Wykres zostanie wygenerowany automatycznie

## Struktura projektu

```
SMW/
├── domain/              # Model domenowy
│   ├── measurement.py   # Klasa Measurement
│   └── point.py         # Klasa MeasurementPoint
├── providers/           # Adaptery źródeł danych
│   ├── base.py          # Protokół DataProvider
│   ├── excel.py         # Provider dla plików Excel
│   └── parsers.py       # Narzędzia parsowania
├── visualization/       # Generowanie wykresów
│   └── plots.py         # Funkcja plot_water_quality
├── gui/                 # Interfejs użytkownika
│   └── app.py           # Aplikacja Streamlit
├── tests/               # Testy jednostkowe
├── requirements.txt     # Zależności Python
└── CLAUDE.md            # Instrukcje dla AI
```

## Architektura

System składa się z czterech warstw:

1. **Domain Model** - stabilne struktury danych (`Measurement`, `MeasurementPoint`)
2. **Data Providers** - adaptery mapujące źródła danych do modelu domenowego
3. **Visualization** - generowanie wykresów (niezależne od źródła danych)
4. **GUI** - interfejs Streamlit (nie zawiera logiki domenowej)

## Testy

```bash
pytest tests/ -v
```

## Format danych Excel

Plik Excel musi zawierać:
- Arkusz `Punkty` z listą punktów pomiarowych
- Osobny arkusz dla każdego punktu z danymi pomiarowymi

## Dokumentacja

- `PRD.md` - opis produktu i wymagania funkcjonalne
- `ARCHITECTURE.md` - szczegóły architektury
- `IMPLEMENTATION_PROMPT.md` - instrukcje implementacyjne
- `RULES.md` - reguły techniczne i standardy

## Licencja

Projekt prywatny.
