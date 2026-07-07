from pathlib import Path
import cv2
import numpy as np
import pandas as pd

from data_cleaning.pipeline import run_cleaning_pipeline
from data_cleaning.column_mapping import standardize_column_names
from data_cleaning.harmonization import harmonize_text_values


def test_standardize_column_names():
    df = pd.DataFrame({"filename": ["root.png"], "sample id": ["S001"]})
    result, events = standardize_column_names(df)

    assert "image_name" in result.columns
    assert "sample_id" in result.columns
    assert any(event["reason"] == "COLUMN_RENAMED" for event in events)


def test_trim_text_values():
    df = pd.DataFrame({"image_name": [" root.png "], "sample_id": [" S001 "]})
    result, events = harmonize_text_values(df)

    assert result.loc[0, "image_name"] == "root.png"
    assert result.loc[0, "sample_id"] == "S001"
    assert len(events) == 2


def test_cleaning_pipeline_creates_manifest_and_audit(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    metadata_path = tmp_path / "raw_metadata.csv"
    output_dir = tmp_path / "out"

    image = np.ones((20, 30, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(images_dir / "root.png"), image)

    metadata_path.write_text("image_name,sample_id\n root.png , S001 \nmissing.png,S002\n", encoding="utf-8")

    manifest, audit_events, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    assert len(manifest) == 2
    assert (manifest["record_status"] == "valid").sum() == 1
    assert (manifest["record_status"] == "rejected").sum() == 1
    assert paths["clean_manifest"].exists()
    assert paths["audit_log"].exists()
    assert len(audit_events) > 0
def test_cleaning_pipeline_audit_log_records_text_harmonization(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    metadata_path = tmp_path / "raw_metadata.csv"
    output_dir = tmp_path / "out"

    image = np.ones((20, 30, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(images_dir / "root.png"), image)

    metadata_path.write_text(
        "image_name,sample_id\n root.png , S001 \n",
        encoding="utf-8",
    )

    _, audit_events, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    audit_log = pd.read_csv(paths["audit_log"])

    assert any(audit_log["rule_id"] == "R002_TRIM_TEXT_VALUES")
    assert any(audit_log["reason"] == "VALUE_STANDARDIZED")
    assert any(audit_log["step"] == "harmonize_text_values")
    assert len(audit_events) == len(audit_log)

def test_harmonize_text_values_records_empty_value_normalization():
    df = pd.DataFrame({"image_name": ["root.png"], "sample_id": ["   "]})

    result, events = harmonize_text_values(df)

    assert pd.isna(result.loc[0, "sample_id"])
    assert len(events) == 1
    assert events[0]["rule_id"] == "R003_NORMALIZE_EMPTY_VALUES"
    assert events[0]["reason"] == "EMPTY_VALUE_NORMALIZED"
    assert events[0]["step"] == "harmonize_text_values"
    assert events[0]["action"] == "normalize_value"

def test_validate_required_values_records_missing_image_name_and_sample_id():
    from data_cleaning.validation import validate_required_values

    df = pd.DataFrame(
        {
            "image_name": ["", "root.png"],
            "sample_id": ["S001", ""],
        }
    )

    events = validate_required_values(df)

    assert len(events) == 2
    assert events[0]["reason"] == "MISSING_IMAGE_NAME"
    assert events[0]["rule_id"] == "R005_VALIDATE_REQUIRED_VALUES"
    assert events[0]["status"] == "failed"
    assert events[0]["action"] == "validate"

    assert events[1]["reason"] == "MISSING_SAMPLE_ID"
    assert events[1]["rule_id"] == "R005_VALIDATE_REQUIRED_VALUES"
    assert events[1]["status"] == "failed"
    assert events[1]["action"] == "validate"

def test_cleaning_pipeline_exports_rejected_records_with_reason(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    metadata_path = tmp_path / "raw_metadata.csv"
    output_dir = tmp_path / "out"

    metadata_path.write_text(
        "image_name,sample_id\nmissing.png,S002\n",
        encoding="utf-8",
    )

    _, _, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    rejected_records = pd.read_csv(paths["rejected_records"])

    assert len(rejected_records) == 1
    assert rejected_records.loc[0, "image_name_clean"] == "missing.png"
    assert rejected_records.loc[0, "record_status"] == "rejected"
    assert rejected_records.loc[0, "reason"] == "MISSING_FILE"

def test_cleaning_summary_counts_rejected_and_missing_files(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    metadata_path = tmp_path / "raw_metadata.csv"
    output_dir = tmp_path / "out"

    metadata_path.write_text(
        "image_name,sample_id\nmissing.png,S002\n",
        encoding="utf-8",
    )

    _, _, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    summary = pd.read_csv(paths["cleaning_summary"])
    summary_values = dict(zip(summary["metric"], summary["value"]))

    assert summary_values["total_records"] == 1
    assert summary_values["valid_records"] == 0
    assert summary_values["rejected_records"] == 1
    assert summary_values["missing_files"] == 1

def test_audit_log_records_missing_file_rejection(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    metadata_path = tmp_path / "raw_metadata.csv"
    metadata_path.write_text(
        "image_name,sample_id\n"
        "missing.png,S001\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "cleaning_output"

    run_cleaning_pipeline(
        metadata_path=metadata_path,
        images_dir=images_dir,
        output_dir=output_dir,
    )

    audit_log = pd.read_csv(output_dir / "audit_log.csv")

    missing_file_events = audit_log[
        (audit_log["reason"] == "MISSING_FILE")
        & (audit_log["step"] == "validate_image_exists")
        & (audit_log["status"] == "failed")
    ]

    assert len(missing_file_events) == 1

    event = missing_file_events.iloc[0]
    assert event["rule_id"] == "R008_VALIDATE_IMAGE_EXISTS"
    assert event["action"] == "validate"
    assert event["image_name"] == "missing.png"
    assert event["sample_id"] == "S001"
    assert "Image file not found at path:" in event["message"]

def test_audit_log_records_unsupported_format_rejection(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    metadata_path = tmp_path / "raw_metadata.csv"
    metadata_path.write_text(
        "image_name,sample_id\n"
        "root.txt,S001\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "cleaning_output"

    run_cleaning_pipeline(
        metadata_path=metadata_path,
        images_dir=images_dir,
        output_dir=output_dir,
    )

    audit_log = pd.read_csv(output_dir / "audit_log.csv")

    unsupported_format_events = audit_log[
        (audit_log["reason"] == "UNSUPPORTED_FORMAT")
        & (audit_log["step"] == "validate_file_extension")
        & (audit_log["status"] == "failed")
    ]

    assert len(unsupported_format_events) == 1

    event = unsupported_format_events.iloc[0]
    assert event["rule_id"] == "R007_VALIDATE_FILE_EXTENSION"
    assert event["action"] == "validate"
    assert event["image_name"] == "root.txt"
    assert event["sample_id"] == "S001"
    assert event["input_value"] == "txt"
    assert "Unsupported image format: txt" in event["message"]

def test_audit_log_records_corrupted_image_rejection(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    broken_image = images_dir / "broken.png"
    broken_image.write_text(
        "this is not a real image file",
        encoding="utf-8",
    )

    metadata_path = tmp_path / "raw_metadata.csv"
    metadata_path.write_text(
        "image_name,sample_id\n"
        "broken.png,S001\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "cleaning_output"

    run_cleaning_pipeline(
        metadata_path=metadata_path,
        images_dir=images_dir,
        output_dir=output_dir,
    )

    audit_log = pd.read_csv(output_dir / "audit_log.csv")

    corrupted_image_events = audit_log[
        (audit_log["reason"] == "CORRUPTED_IMAGE")
        & (audit_log["step"] == "validate_image_readable")
        & (audit_log["status"] == "failed")
    ]

    assert len(corrupted_image_events) == 1

    event = corrupted_image_events.iloc[0]
    assert event["rule_id"] == "R009_VALIDATE_IMAGE_READABLE"
    assert event["action"] == "read_image"
    assert event["image_name"] == "broken.png"
    assert event["sample_id"] == "S001"
    assert "Image could not be opened" in event["message"]

def test_cleaning_summary_counts_unsupported_formats(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    metadata_path = tmp_path / "raw_metadata.csv"
    metadata_path.write_text(
        "image_name,sample_id\n"
        "root.txt,S001\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "out"

    _, _, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    summary = pd.read_csv(paths["cleaning_summary"])
    summary_values = dict(zip(summary["metric"], summary["value"]))

    assert summary_values["total_records"] == 1
    assert summary_values["valid_records"] == 0
    assert summary_values["rejected_records"] == 1
    assert summary_values["unsupported_formats"] == 1
    assert summary_values["missing_files"] == 0
    assert summary_values["corrupted_images"] == 0

def test_cleaning_summary_counts_corrupted_images(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    broken_image = images_dir / "broken.png"
    broken_image.write_text(
        "this is not a real image file",
        encoding="utf-8",
    )

    metadata_path = tmp_path / "raw_metadata.csv"
    metadata_path.write_text(
        "image_name,sample_id\n"
        "broken.png,S001\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "out"

    _, _, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    summary = pd.read_csv(paths["cleaning_summary"])
    summary_values = dict(zip(summary["metric"], summary["value"]))

    assert summary_values["total_records"] == 1
    assert summary_values["valid_records"] == 0
    assert summary_values["rejected_records"] == 1
    assert summary_values["corrupted_images"] == 1
    assert summary_values["missing_files"] == 0
    assert summary_values["unsupported_formats"] == 0

def test_rejected_records_contains_unsupported_format_reason(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    metadata_path = tmp_path / "raw_metadata.csv"
    metadata_path.write_text(
        "image_name,sample_id\n"
        "root.txt,S001\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "out"

    _, _, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    rejected_records = pd.read_csv(paths["rejected_records"])

    assert len(rejected_records) == 1
    assert rejected_records.loc[0, "record_status"] == "rejected"
    assert rejected_records.loc[0, "reason"] == "UNSUPPORTED_FORMAT"
    assert rejected_records.loc[0, "image_name_clean"] == "root.txt"
    assert rejected_records.loc[0, "sample_id_clean"] == "S001"

def test_rejected_records_contains_corrupted_image_reason(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    broken_image = images_dir / "broken.png"
    broken_image.write_text(
        "this is not a real image file",
        encoding="utf-8",
    )

    metadata_path = tmp_path / "raw_metadata.csv"
    metadata_path.write_text(
        "image_name,sample_id\n"
        "broken.png,S001\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "out"

    _, _, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    rejected_records = pd.read_csv(paths["rejected_records"])

    assert len(rejected_records) == 1
    assert rejected_records.loc[0, "record_status"] == "rejected"
    assert rejected_records.loc[0, "reason"] == "CORRUPTED_IMAGE"
    assert rejected_records.loc[0, "image_name_clean"] == "broken.png"
    assert rejected_records.loc[0, "sample_id_clean"] == "S001"

def test_clean_manifest_keeps_unsupported_format_rejection(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    metadata_path = tmp_path / "raw_metadata.csv"
    metadata_path.write_text(
        "image_name,sample_id\n"
        "root.txt,S001\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "out"

    _, _, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    manifest = pd.read_csv(paths["clean_manifest"])

    assert len(manifest) == 1
    assert manifest.loc[0, "record_status"] == "rejected"
    assert manifest.loc[0, "reason"] == "UNSUPPORTED_FORMAT"
    assert manifest.loc[0, "image_name_clean"] == "root.txt"
    assert manifest.loc[0, "sample_id_clean"] == "S001"
    assert manifest.loc[0, "is_valid"] == False

def test_clean_manifest_keeps_corrupted_image_rejection(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    broken_image = images_dir / "broken.png"
    broken_image.write_text(
        "this is not a real image file",
        encoding="utf-8",
    )

    metadata_path = tmp_path / "raw_metadata.csv"
    metadata_path.write_text(
        "image_name,sample_id\n"
        "broken.png,S001\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "out"

    _, _, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    manifest = pd.read_csv(paths["clean_manifest"])

    assert len(manifest) == 1
    assert manifest.loc[0, "record_status"] == "rejected"
    assert manifest.loc[0, "reason"] == "CORRUPTED_IMAGE"
    assert manifest.loc[0, "image_name_clean"] == "broken.png"
    assert manifest.loc[0, "sample_id_clean"] == "S001"
    assert manifest.loc[0, "is_valid"] == False

def test_clean_manifest_audit_events_count_matches_audit_log(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    metadata_path = tmp_path / "raw_metadata.csv"
    metadata_path.write_text(
        "image_name,sample_id\n"
        "missing.png,S001\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "out"

    _, _, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    manifest = pd.read_csv(paths["clean_manifest"])
    audit_log = pd.read_csv(paths["audit_log"])

    record_id = manifest.loc[0, "record_id"]

    audit_events_for_record = audit_log[
        audit_log["record_id"].astype(str) == str(record_id)
    ]

    assert len(manifest) == 1
    assert len(audit_events_for_record) > 0
    assert manifest.loc[0, "audit_events_count"] == len(audit_events_for_record)

def test_clean_manifest_records_valid_image_metadata(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    image = np.ones((20, 30, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(images_dir / "valid.png"), image)

    metadata_path = tmp_path / "raw_metadata.csv"
    metadata_path.write_text(
        "image_name,sample_id\n"
        "valid.png,S001\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "out"

    _, _, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    manifest = pd.read_csv(paths["clean_manifest"])

    assert len(manifest) == 1
    assert manifest.loc[0, "record_status"] == "valid"
    assert manifest.loc[0, "reason"] == "OK"
    assert manifest.loc[0, "is_valid"] == True
    assert manifest.loc[0, "image_name_clean"] == "valid.png"
    assert manifest.loc[0, "sample_id_clean"] == "S001"
    assert manifest.loc[0, "file_format"] == "png"
    assert manifest.loc[0, "width_px"] == 30
    assert manifest.loc[0, "height_px"] == 20
    assert manifest.loc[0, "audit_events_count"] > 0

def test_audit_log_records_valid_image_dimensions(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    image = np.ones((20, 30, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(images_dir / "valid.png"), image)

    metadata_path = tmp_path / "raw_metadata.csv"
    metadata_path.write_text(
        "image_name,sample_id\n"
        "valid.png,S001\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "out"

    _, _, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    audit_log = pd.read_csv(paths["audit_log"])

    dimension_events = audit_log[
        (audit_log["step"] == "extract_image_dimensions")
        & (audit_log["status"] == "success")
        & (audit_log["reason"] == "OK")
    ]

    assert len(dimension_events) == 1

    event = dimension_events.iloc[0]
    assert event["rule_id"] == "R010_EXTRACT_IMAGE_DIMENSIONS"
    assert event["action"] == "extract_metadata"
    assert event["image_name"] == "valid.png"
    assert event["sample_id"] == "S001"
    assert event["output_value"] == "30x20"
    assert event["message"] == "Image dimensions extracted"

def test_cleaning_summary_counts_valid_image(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    image = np.ones((20, 30, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(images_dir / "valid.png"), image)

    metadata_path = tmp_path / "raw_metadata.csv"
    metadata_path.write_text(
        "image_name,sample_id\n"
        "valid.png,S001\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "out"

    _, _, paths = run_cleaning_pipeline(metadata_path, images_dir, output_dir)

    summary = pd.read_csv(paths["cleaning_summary"])
    summary_values = dict(zip(summary["metric"], summary["value"]))

    assert summary_values["total_records"] == 1
    assert summary_values["valid_records"] == 1
    assert summary_values["warning_records"] == 0
    assert summary_values["rejected_records"] == 0
    assert summary_values["missing_files"] == 0
    assert summary_values["unsupported_formats"] == 0
    assert summary_values["corrupted_images"] == 0

