# Transparency Principles

Główna zasada projektu:

```text
No silent transformations.
No silent exclusions.
No silent measurements.
```

## Co to oznacza?

- Każda zmiana danych wejściowych musi być zapisana w `audit_log.csv`.
- Każde odrzucenie rekordu musi mieć `reason` i `message`.
- Każdy parametr analizy obrazu musi być zapisany w `processing_log.csv`.
- Każdy pomiar w `root_measurements.csv` musi pochodzić z jawnego kroku przetwarzania.
- `clean_manifest.csv` zawiera również rekordy odrzucone, żeby nic nie znikało po cichu.
