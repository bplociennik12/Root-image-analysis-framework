from pathlib import Path
import cv2
import pandas as pd

from data_cleaning.audit import make_audit_event
from data_cleaning.config import SUPPORTED_IMAGE_FORMATS


def build_image_path(images_dir: str | Path, image_name: str) -> Path:
    return Path(images_dir) / str(image_name)


def validate_images(df: pd.DataFrame, images_dir: str | Path) -> tuple[pd.DataFrame, list[dict]]:
    result = df.copy()
    events = []

    result["image_path"] = ""
    result["file_format"] = ""
    result["width_px"] = 0
    result["height_px"] = 0

    for row_index, row in result.iterrows():
        image_name = row.get("image_name", "")
        sample_id = row.get("sample_id", "")
        image_path = build_image_path(images_dir, image_name) if not pd.isna(image_name) else Path(images_dir)

        result.at[row_index, "image_path"] = str(image_path)
        events.append(
            make_audit_event(
                record_id=row_index,
                image_name=str(image_name),
                sample_id=str(sample_id),
                step="build_image_path",
                rule_id="R006_BUILD_IMAGE_PATH",
                rule_description="Build image_path from images_dir and image_name",
                input_value=str(image_name),
                output_value=str(image_path),
                action="build_path",
                status="success",
                reason="OK",
                message="Image path built",
            )
        )

        suffix = image_path.suffix.lower().replace(".", "")
        result.at[row_index, "file_format"] = suffix

        if suffix not in SUPPORTED_IMAGE_FORMATS:
            events.append(
                make_audit_event(
                    record_id=row_index,
                    image_name=str(image_name),
                    sample_id=str(sample_id),
                    step="validate_file_extension",
                    rule_id="R007_VALIDATE_FILE_EXTENSION",
                    rule_description="Image extension must be supported",
                    input_value=suffix,
                    output_value="",
                    action="validate",
                    status="failed",
                    reason="UNSUPPORTED_FORMAT",
                    message=f"Unsupported image format: {suffix}",
                )
            )
            continue

        if not image_path.exists():
            events.append(
                make_audit_event(
                    record_id=row_index,
                    image_name=str(image_name),
                    sample_id=str(sample_id),
                    step="validate_image_exists",
                    rule_id="R008_VALIDATE_IMAGE_EXISTS",
                    rule_description="Image file must exist",
                    input_value=str(image_path),
                    output_value="",
                    action="validate",
                    status="failed",
                    reason="MISSING_FILE",
                    message=f"Image file not found at path: {image_path}",
                )
            )
            continue

        image = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
        if image is None:
            events.append(
                make_audit_event(
                    record_id=row_index,
                    image_name=str(image_name),
                    sample_id=str(sample_id),
                    step="validate_image_readable",
                    rule_id="R009_VALIDATE_IMAGE_READABLE",
                    rule_description="Image must be readable",
                    input_value=str(image_path),
                    output_value="",
                    action="read_image",
                    status="failed",
                    reason="CORRUPTED_IMAGE",
                    message="Image could not be opened",
                )
            )
            continue

        height, width = image.shape[:2]
        result.at[row_index, "width_px"] = int(width)
        result.at[row_index, "height_px"] = int(height)
        events.append(
            make_audit_event(
                record_id=row_index,
                image_name=str(image_name),
                sample_id=str(sample_id),
                step="extract_image_dimensions",
                rule_id="R010_EXTRACT_IMAGE_DIMENSIONS",
                rule_description="Extract image width and height",
                input_value=str(image_path),
                output_value=f"{width}x{height}",
                action="extract_metadata",
                status="success",
                reason="OK",
                message="Image dimensions extracted",
            )
        )

    return result, events
