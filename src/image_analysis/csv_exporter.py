from pathlib import Path
import pandas as pd

from shared.schemas import PROCESSING_LOG_COLUMNS, ROOT_MEASUREMENTS_COLUMNS


def export_analysis_outputs(
    measurements: list[dict],
    processing_events: list[dict],
    output_dir: str | Path,
) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    measurements_path = output / "root_measurements.csv"
    processing_log_path = output / "processing_log.csv"
    summary_path = output / "analysis_summary.csv"

    measurements_df = pd.DataFrame(measurements).reindex(columns=ROOT_MEASUREMENTS_COLUMNS)
    measurements_df.to_csv(measurements_path, index=False)

    pd.DataFrame(processing_events).reindex(columns=PROCESSING_LOG_COLUMNS).to_csv(processing_log_path, index=False)

    summary = pd.DataFrame(
        [
            {"metric": "input_records", "value": len(measurements_df)},
            {"metric": "analysis_success", "value": int((measurements_df["processing_status"] == "success").sum())},
            {"metric": "analysis_warning", "value": int((measurements_df["processing_status"] == "warning").sum())},
            {"metric": "analysis_failed", "value": int((measurements_df["processing_status"] == "failed").sum())},
            {"metric": "empty_masks", "value": int((measurements_df["reason"] == "EMPTY_MASK").sum())},
            {"metric": "multiple_components", "value": int((measurements_df["reason"] == "MULTIPLE_COMPONENTS").sum())},
            {"metric": "mean_area_px", "value": float(measurements_df["area_px"].mean()) if len(measurements_df) else 0},
            {"metric": "mean_skeleton_length_px", "value": float(measurements_df["skeleton_length_px"].mean()) if len(measurements_df) else 0},
        ]
    )
    summary.to_csv(summary_path, index=False)

    return {
        "root_measurements": measurements_path,
        "processing_log": processing_log_path,
        "analysis_summary": summary_path,
    }
