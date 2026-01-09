# System Wizualizacji Parametrow Jakosci Wod

Przegladarkowe narzedzie do wizualizacji danych pomiarowych jakosci wod powierzchniowych.

## Opis

System umozliwia wizualizacje zmiennosci parametrow fizykochemicznych wod na podstawie danych z roznych zrodel (Excel, CSV, API). Architektura oparta na warstwach zapewnia niezaleznosc wizualizacji od formatu danych zrodlowych.

### Glowne funkcje

- Wczytywanie danych z plikow Excel
- Wybor punktu pomiarowego
- Dwa typy wykresow:
  - **Wykres liniowy** - parametry fizykochemiczne:
    - Temperatura wody (0-30°C)
    - pH (5-9)
    - Tlen rozpuszczony (0-15 mg/L)
    - Przewodnosc elektrolityczna (0-3500 µS/cm)
  - **Wykres punktowy** - zwiazki chemiczne:
    - Azotany, azotyny, fosforany, chlorki, siarczany
- Obsluga flag pomiarowych (`<`, `>`) - wartosci poza zakresem pomiaru sa wyroznionie czarna obwodka
- Tryb batch - generowanie wykresow dla wielu plikow naraz z pobraniem ZIP

## Wymagania

- Python 3.12+

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone https://github.com/Daldek/SMW.git
cd SMW
```

2. Utworz i aktywuj srodowisko wirtualne:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# lub
.venv\Scripts\activate     # Windows
```

3. Zainstaluj pakiet w trybie edytowalnym:
```bash
pip install -e .
```

## Uruchomienie

```bash
streamlit run gui/app.py
```

Aplikacja otworzy sie w przegladarce pod adresem `http://localhost:8501`.

## Uzytkowanie

### Tryb pojedynczego pliku

1. Zaladuj plik Excel z danymi pomiarowymi
2. Wybierz punkt pomiarowy z listy
3. Wykresy zostana wygenerowane automatycznie

### Tryb batch (generowanie z folderu)

1. Przejdz do zakladki "Generowanie z folderu"
2. Zaladuj wiele plikow Excel
3. Kliknij "Generuj wykresy"
4. Pobierz archiwum ZIP z wszystkimi wykresami

## Struktura projektu

```
SMW/
├── domain/              # Model domenowy
│   ├── measurement.py   # Klasa Measurement
│   └── point.py         # Klasa MeasurementPoint
├── providers/           # Adaptery zrodel danych
│   ├── base.py          # Protokol DataProvider
│   ├── excel.py         # Provider dla plikow Excel
│   └── parsers.py       # Narzedzia parsowania
├── visualization/       # Generowanie wykresow
│   └── plots.py         # Funkcje plot_water_quality, plot_chemical_parameters
├── gui/                 # Interfejs uzytkownika
│   └── app.py           # Aplikacja Streamlit
├── tests/               # Testy jednostkowe
├── pyproject.toml       # Konfiguracja pakietu
├── requirements.txt     # Zaleznosci Python
└── CLAUDE.md            # Instrukcje dla AI
```

## Architektura

System sklada sie z czterech warstw:

1. **Domain Model** - stabilne struktury danych (`Measurement`, `MeasurementPoint`)
2. **Data Providers** - adaptery mapujace zrodla danych do modelu domenowego
3. **Visualization** - generowanie wykresow (niezalezne od zrodla danych)
4. **GUI** - interfejs Streamlit (nie zawiera logiki domenowej)

## Testy

```bash
pytest tests/ -v
```

## Format danych Excel

Plik Excel musi zawierac:
- Arkusz `Punkty` z lista punktow pomiarowych (kolumny: Kod punktu, Nazwa punktu, itp.)
- Osobny arkusz dla kazdego punktu z danymi pomiarowymi

Obslugiwane formaty wartosci:
- Liczby: `1.23`, `1,23`
- Flagi zakresu: `<0.05`, `>100`

## Dokumentacja

- `PRD.md` - opis produktu i wymagania funkcjonalne
- `ARCHITECTURE.md` - szczegoly architektury
- `IMPLEMENTATION_PROMPT.md` - instrukcje implementacyjne
- `RULES.md` - reguly techniczne i standardy

## Licencja

Projekt prywatny.
