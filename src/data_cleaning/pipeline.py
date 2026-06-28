from pathlib import Path

from data_cleaning.column_mapping import standardize_column_names
from data_cleaning.exporters import export_cleaning_outputs
from data_cleaning.harmonization import harmonize_text_values
from data_cleaning.image_validation import validate_images
from data_cleaning.load_metadata import load_raw_metadata
from data_cleaning.manifest import build_clean_manifest
from data_cleaning.validation import validate_required_columns, validate_required_values


def run_cleaning_pipeline(metadata_path: str | Path, images_dir: str | Path, output_dir: str | Path):
    audit_events = []

    raw_df = load_raw_metadata(metadata_path)
    df = raw_df.copy()

    if "image_name" in df.columns:
        df["image_name_original"] = df["image_name"]
    if "sample_id" in df.columns:
        df["sample_id_original"] = df["sample_id"]

    df, events = standardize_column_names(df)
    audit_events.extend(events)

    if "image_name_original" not in df.columns and "image_name" in df.columns:
        df["image_name_original"] = df["image_name"]
    if "sample_id_original" not in df.columns and "sample_id" in df.columns:
        df["sample_id_original"] = df["sample_id"]

    audit_events.extend(validate_required_columns(df))

    df, events = harmonize_text_values(df)
    audit_events.extend(events)

    audit_events.extend(validate_required_values(df))

    df, events = validate_images(df, images_dir)
    audit_events.extend(events)

    manifest = build_clean_manifest(df, audit_events)
    paths = export_cleaning_outputs(manifest, audit_events, output_dir)

    return manifest, audit_events, paths
