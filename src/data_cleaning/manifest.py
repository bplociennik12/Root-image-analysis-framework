import pandas as pd

from shared.statuses import VALID, REJECTED


REJECTION_REASONS = {
    "MISSING_REQUIRED_COLUMN",
    "MISSING_IMAGE_NAME",
    "MISSING_SAMPLE_ID",
    "MISSING_FILE",
    "UNSUPPORTED_FORMAT",
    "CORRUPTED_IMAGE",
}


def _events_by_record(events: list[dict]) -> dict:
    grouped = {}
    for event in events:
        record_id = event.get("record_id")
        grouped.setdefault(record_id, []).append(event)
    return grouped


def build_clean_manifest(df: pd.DataFrame, audit_events: list[dict]) -> pd.DataFrame:
    events_by_record = _events_by_record(audit_events)
    global_failures = [
        event for event in audit_events
        if event.get("record_id") == "ALL" and event.get("status") == "failed"
    ]

    rows = []
    for row_index, row in df.iterrows():
        row_events = events_by_record.get(row_index, []) + global_failures
        failed_events = [e for e in row_events if e.get("reason") in REJECTION_REASONS]

        if failed_events:
            status = REJECTED
            reason = failed_events[0]["reason"]
            message = failed_events[0]["message"]
            is_valid = False
        else:
            status = VALID
            reason = "OK"
            message = "Record is ready for analysis"
            is_valid = True

        image_name_clean = row.get("image_name", "")
        sample_id_clean = row.get("sample_id", "")
        rows.append(
            {
                "record_id": row_index,
                "image_id": f"IMG_{row_index + 1:04d}",
                "image_name_original": row.get("image_name_original", image_name_clean),
                "image_name_clean": image_name_clean,
                "image_path": row.get("image_path", ""),
                "sample_id_original": row.get("sample_id_original", sample_id_clean),
                "sample_id_clean": sample_id_clean,
                "file_format": row.get("file_format", ""),
                "width_px": int(row.get("width_px", 0) or 0),
                "height_px": int(row.get("height_px", 0) or 0),
                "is_valid": is_valid,
                "record_status": status,
                "reason": reason,
                "message": message,
                "audit_events_count": len(row_events),
            }
        )
    return pd.DataFrame(rows)
