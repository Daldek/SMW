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
- Eksport wynikow do CSV (wszystkie punkty, wspolrzedne, ostatnie pomiary)
  - Tryb pojedynczego pliku - eksport + aktualizacja istniejacego CSV (merge)
  - Tryb batch - zbiorczy CSV z deduplikacja + CSV bledow

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
4. W sekcji "Eksport CSV" pobierz plik `wyniki.csv` ze wszystkimi punktami
   - Opcjonalnie zaladuj istniejacy CSV, aby zaktualizowac go o nowe dane

### Tryb batch (generowanie z folderu)

1. Przejdz do zakladki "Generowanie z folderu"
2. Podaj sciezke do folderu (lub uzyj przycisku "Wybierz folder")
3. Kliknij "Generuj wykresy"
4. Pobierz archiwum ZIP z wykresami, plik `wyniki.csv` z danymi oraz `error_wyniki.csv` z bledami

## Struktura projektu

```
SMW/
├── domain/              # Model domenowy
│   ├── measurement.py   # Klasa Measurement
│   └── point.py         # Klasa MeasurementPoint
├── providers/           # Adaptery zrodel danych
│   ├── base.py          # Protokol DataProvider
│   ├── excel.py         # Provider dla plikow Excel
│   ├── exceptions.py    # Wyjatki providerow
│   └── parsers.py       # Narzedzia parsowania
├── exporters/           # Eksport danych wyjsciowych
│   └── csv_exporter.py  # Eksport do CSV (wyniki + bledy)
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

Obslugiwane formaty wspolrzednych:
- `52.213396, 21.185913` (kropki dziesietne, przecinek jako separator)
- `52,2297 21,0122` (przecinki dziesietne, spacja jako separator)
- `52,2297;21,0122` (srednik jako separator)
- `50,33558° N, 19,94761° E` (symbole stopni i kierunki geograficzne)

### Format CSV wyjsciowego

Kolumny w `wyniki.csv`:
```
point_id, point_name, river_name, jcwp_code, catchment_authority, rzgw,
latitude, longitude, timestamp, water_temperature, transparency,
dissolved_oxygen, nitrates, nitrites, phosphates, chlorides, sulphates,
pH, water_temperature_home, conductivity
```

- Wartosci z flagami jako tekst: `<0.05`, `>100`
- Brak wartosci = puste pole
- Kodowanie UTF-8 z BOM (kompatybilnosc z Excelem)

## Dokumentacja

- `PRD.md` - opis produktu i wymagania funkcjonalne
- `ARCHITECTURE.md` - szczegoly architektury
- `IMPLEMENTATION_PROMPT.md` - instrukcje implementacyjne
- `RULES.md` - reguly techniczne i standardy

## Licencja

Projekt prywatny.
