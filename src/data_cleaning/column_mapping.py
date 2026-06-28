import pandas as pd

from data_cleaning.audit import make_audit_event

COLUMN_ALIASES = {
    "image_name": {"image_name", "image", "image file", "image_file", "filename", "file", "file_name"},
    "sample_id": {"sample_id", "sample", "sample id", "sampleid", "plant_id", "plant id"},
}


def _normalize_column_name(name: str) -> str:
    return str(name).strip().lower().replace("-", "_")


def standardize_column_names(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    renamed = {}
    events = []

    for col in df.columns:
        normalized = _normalize_column_name(col).replace("_", " ")
        target = None
        for standard, aliases in COLUMN_ALIASES.items():
            if normalized in aliases:
                target = standard
                break

        if target and col != target:
            renamed[col] = target
            events.append(
                make_audit_event(
                    record_id="ALL",
                    step="standardize_column_names",
                    rule_id="R001_STANDARDIZE_COLUMN_NAMES",
                    rule_description="Map raw column names to standard schema",
                    input_value=col,
                    output_value=target,
                    action="rename_column",
                    status="success",
                    reason="COLUMN_RENAMED",
                    message="Column renamed successfully",
                )
            )

    return df.rename(columns=renamed), events
