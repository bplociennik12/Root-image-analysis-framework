# Project Plan

## Cel MVP

Zbudować dwa stabilne pipeline’y terminalowe:

```text
raw_metadata.csv + image folder
→ clean_manifest.csv + rejected_records.csv + audit_log.csv + cleaning_summary.csv
```

oraz:

```text
clean_manifest.csv
→ root_measurements.csv + processing_log.csv + analysis_summary.csv + masks + skeletons + overlays
```

## Etapy

1. Dokumentacja i kontrakty danych.
2. Szkielet repozytorium.
3. Data Cleaning MVP.
4. Testy Data Cleaning App.
5. Image Analysis MVP.
6. Testy Image Analysis App.
7. Raporty Markdown.
8. GUI PySide6 jako Future Development.

## Poza MVP

Nie dodajemy na starcie: deep learning, U-Net, Mask R-CNN, klasyfikacji gatunków, predykcji zdrowia roślin, analizy 3D, GUI, PDF, bazy danych ani fuzzy matching.
