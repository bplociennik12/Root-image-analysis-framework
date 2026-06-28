# Root Image Analysis Framework

Edukacyjno-badawczy framework w Pythonie do transparentnego czyszczenia danych i powtarzalnej analizy obrazów 2D korzeni roślin.

Projekt składa się z dwóch terminalowych pipeline’ów:

1. **Data Cleaning, Harmonization and Audit App**
   - wejście: `raw_metadata.csv` + folder obrazów,
   - wyjście: `clean_manifest.csv`, `rejected_records.csv`, `audit_log.csv`, `cleaning_summary.csv`.

2. **Root Image Analysis App**
   - wejście: `clean_manifest.csv`,
   - wyjście: `root_measurements.csv`, `processing_log.csv`, `analysis_summary.csv`, maski, szkielety i overlaye.

## Główna zasada

```text
No silent transformations.
No silent exclusions.
No silent measurements.
```

Każda zmiana danych, odrzucenie rekordu, parametr przetwarzania obrazu i obliczona miara musi mieć ślad w plikach CSV lub dokumentacji.

## Instalacja

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Uruchomienie czyszczenia danych

```bash
python -m data_cleaning.main --metadata data/demo/metadata/raw_metadata.csv --images data/demo/images --output outputs/cleaning
```

## Uruchomienie analizy obrazów

```bash
python -m image_analysis.main --manifest outputs/cleaning/clean_manifest.csv --output outputs/analysis
```

## Testy

```bash
python -m pytest -q
```

Jeśli projekt nie jest zainstalowany jako pakiet:

```bash
PYTHONPATH=src python -m pytest -q
```

Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m pytest -q
```

## Ograniczenia

Projekt analizuje obrazy 2D korzeni i raportuje cechy morfologiczne wyprowadzone z obrazu.
Nie diagnozuje zdrowia roślin ani nie wnioskuje bezpośrednio o stanie biologicznym.
Wyniki zależą od jakości obrazu, tła, kontrastu, parametrów segmentacji i kalibracji.
Bez kalibracji skali pomiary są raportowane w pikselach.
