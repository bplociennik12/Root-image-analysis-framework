# Cleaning Rules

## R001_STANDARDIZE_COLUMN_NAMES

Mapuje znane warianty nazw kolumn do standardowych nazw.

## R002_TRIM_TEXT_VALUES

Usuwa spacje z początku i końca wartości tekstowych.

## R003_NORMALIZE_EMPTY_VALUES

Zamienia puste stringi na brak danych.

## R004_VALIDATE_REQUIRED_COLUMNS

Sprawdza, czy tabela zawiera wymagane kolumny: `image_name`, `sample_id`.

## R005_VALIDATE_REQUIRED_VALUES

Sprawdza, czy `image_name` i `sample_id` nie są puste.

## R006_BUILD_IMAGE_PATH

Tworzy `image_path` na podstawie `images_dir` i `image_name`.

## R007_VALIDATE_FILE_EXTENSION

Sprawdza, czy rozszerzenie obrazu jest obsługiwane.

## R008_VALIDATE_IMAGE_EXISTS

Sprawdza, czy plik obrazu istnieje.

## R009_VALIDATE_IMAGE_READABLE

Sprawdza, czy obraz można otworzyć.

## R010_EXTRACT_IMAGE_DIMENSIONS

Odczytuje `width_px` i `height_px`.

## R011_ASSIGN_RECORD_STATUS

Ustala finalny status rekordu: `valid`, `warning` albo `rejected`.
