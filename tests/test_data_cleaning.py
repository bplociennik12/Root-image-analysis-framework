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
