from pathlib import Path
import pandas as pd

from shared.schemas import (
    AUDIT_LOG_COLUMNS,
    CLEAN_MANIFEST_COLUMNS,
    REJECTED_RECORDS_COLUMNS,
)


def export_cleaning_outputs(
    manifest: pd.DataFrame,
    audit_events: list[dict],
    output_dir: str | Path,
) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    manifest_path = output / "clean_manifest.csv"
    rejected_path = output / "rejected_records.csv"
    audit_path = output / "audit_log.csv"
    summary_path = output / "cleaning_summary.csv"

    manifest = manifest.reindex(columns=CLEAN_MANIFEST_COLUMNS)
    manifest.to_csv(manifest_path, index=False)

    rejected = manifest[manifest["record_status"] == "rejected"].reindex(columns=REJECTED_RECORDS_COLUMNS)
    rejected.to_csv(rejected_path, index=False)

    pd.DataFrame(audit_events).reindex(columns=AUDIT_LOG_COLUMNS).to_csv(audit_path, index=False)

    summary = pd.DataFrame(
        [
            {"metric": "total_records", "value": len(manifest)},
            {"metric": "valid_records", "value": int((manifest["record_status"] == "valid").sum())},
            {"metric": "warning_records", "value": int((manifest["record_status"] == "warning").sum())},
            {"metric": "rejected_records", "value": int((manifest["record_status"] == "rejected").sum())},
            {"metric": "missing_files", "value": int((manifest["reason"] == "MISSING_FILE").sum())},
            {"metric": "unsupported_formats", "value": int((manifest["reason"] == "UNSUPPORTED_FORMAT").sum())},
            {"metric": "corrupted_images", "value": int((manifest["reason"] == "CORRUPTED_IMAGE").sum())},
            {"metric": "missing_sample_id", "value": int((manifest["reason"] == "MISSING_SAMPLE_ID").sum())},
        ]
    )
    summary.to_csv(summary_path, index=False)

    return {
        "clean_manifest": manifest_path,
        "rejected_records": rejected_path,
        "audit_log": audit_path,
        "cleaning_summary": summary_path,
    }
