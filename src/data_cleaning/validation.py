import pandas as pd

from shared.schemas import REQUIRED_RAW_METADATA_COLUMNS
from data_cleaning.audit import make_audit_event


def validate_required_columns(df: pd.DataFrame) -> list[dict]:
    events = []
    for column in REQUIRED_RAW_METADATA_COLUMNS:
        if column not in df.columns:
            events.append(
                make_audit_event(
                    record_id="ALL",
                    step="validate_required_columns",
                    rule_id="R004_VALIDATE_REQUIRED_COLUMNS",
                    rule_description="Required columns must exist",
                    input_value=",".join(df.columns),
                    output_value=column,
                    action="validate",
                    status="failed",
                    reason="MISSING_REQUIRED_COLUMN",
                    message=f"Required column missing: {column}",
                )
            )
    return events


def validate_required_values(df: pd.DataFrame) -> list[dict]:
    events = []
    for row_index, row in df.iterrows():
        for column, reason in [("image_name", "MISSING_IMAGE_NAME"), ("sample_id", "MISSING_SAMPLE_ID")]:
            value = row.get(column, pd.NA)
            if pd.isna(value) or str(value).strip() == "":
                events.append(
                    make_audit_event(
                        record_id=row_index,
                        image_name=str(row.get("image_name", "")),
                        sample_id=str(row.get("sample_id", "")),
                        step="validate_required_values",
                        rule_id="R005_VALIDATE_REQUIRED_VALUES",
                        rule_description=f"{column} must not be empty",
                        input_value=value,
                        output_value="",
                        action="validate",
                        status="failed",
                        reason=reason,
                        message=f"{column} is required",
                    )
                )
    return events
