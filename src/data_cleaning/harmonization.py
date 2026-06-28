import pandas as pd

from data_cleaning.audit import make_audit_event


def harmonize_text_values(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    result = df.copy()
    events = []

    for row_index, row in result.iterrows():
        for col in result.select_dtypes(include=["object", "string"]).columns:
            value = row[col]
            if pd.isna(value):
                continue

            original = value
            cleaned = str(value).strip()

            if cleaned == "":
                cleaned_value = pd.NA
                reason = "EMPTY_VALUE_NORMALIZED"
                message = "Empty string converted to missing value"
                rule_id = "R003_NORMALIZE_EMPTY_VALUES"
                description = "Convert empty text values to missing values"
                action = "normalize_value"
            else:
                cleaned_value = cleaned
                reason = "VALUE_STANDARDIZED"
                message = "Whitespace removed"
                rule_id = "R002_TRIM_TEXT_VALUES"
                description = "Trim whitespace from text values"
                action = "modify_value"

            if str(original) != str(cleaned_value):
                result.at[row_index, col] = cleaned_value
                events.append(
                    make_audit_event(
                        record_id=row_index,
                        image_name=str(row.get("image_name", "")),
                        sample_id=str(row.get("sample_id", "")),
                        step="harmonize_text_values",
                        rule_id=rule_id,
                        rule_description=description,
                        input_value=original,
                        output_value=cleaned_value,
                        action=action,
                        status="success",
                        reason=reason,
                        message=f"{message}: {col}",
                    )
                )

    return result, events
