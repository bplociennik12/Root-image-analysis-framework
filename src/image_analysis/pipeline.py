from pathlib import Path

from shared.logging_utils import utc_timestamp
from image_analysis import config
from image_analysis.csv_exporter import export_analysis_outputs
from image_analysis.image_exporter import save_mask, save_overlay, save_skeleton
from image_analysis.image_loader import load_image
from image_analysis.load_manifest import load_clean_manifest, select_valid_records, validate_manifest_schema
from image_analysis.morphology import extract_morphological_features
from image_analysis.preprocessing import preprocess_image
from image_analysis.segmentation import clean_mask, segment_root_otsu
from image_analysis.skeletonization import skeletonize_mask


def make_processing_event(record, step, parameter, value, status, reason, message):
    return {
        "timestamp": utc_timestamp(),
        "record_id": record.get("record_id", ""),
        "image_id": record.get("image_id", ""),
        "image_name": record.get("image_name_clean", record.get("image_name", "")),
        "step": step,
        "parameter": parameter,
        "value": value,
        "status": status,
        "reason": reason,
        "message": message,
    }


def _failed_measurement(record, reason, message):
    return {
        "record_id": record.get("record_id", ""),
        "image_id": record.get("image_id", ""),
        "image_name": record.get("image_name_clean", ""),
        "sample_id": record.get("sample_id_clean", ""),
        "roi_used": False,
        "area_px": 0,
        "skeleton_length_px": 0,
        "branch_points_count": 0,
        "endpoints_count": 0,
        "bbox_width_px": 0,
        "bbox_height_px": 0,
        "aspect_ratio": 0.0,
        "centroid_x_px": 0.0,
        "centroid_y_px": 0.0,
        "component_count": 0,
        "processing_status": "failed",
        "reason": reason,
        "message": message,
    }


def run_analysis_pipeline(
    manifest_path: str | Path,
    output_dir: str | Path,
    foreground: str = config.FOREGROUND,
):
    manifest = load_clean_manifest(manifest_path)
    missing_columns = validate_manifest_schema(manifest)
    if missing_columns:
        raise ValueError(f"Manifest is missing required columns: {missing_columns}")

    valid_records = select_valid_records(manifest)
    measurements = []
    processing_events = []

    output = Path(output_dir)
    masks_dir = output / "masks"
    skeletons_dir = output / "skeletons"
    overlays_dir = output / "overlays"

    for _, record in valid_records.iterrows():
        record_dict = record.to_dict()

        try:
            processing_events.append(make_processing_event(record_dict, "load_image", "path", record["image_path"], "success", "OK", "Loading image"))
            image = load_image(record["image_path"])

            processing_events.append(make_processing_event(record_dict, "preprocessing", "grayscale", True, "success", "OK", "Image converted to grayscale"))
            processing_events.append(make_processing_event(record_dict, "preprocessing", "gaussian_blur_kernel", config.GAUSSIAN_BLUR_KERNEL, "success", "OK", "Gaussian blur applied"))
            preprocessed = preprocess_image(image, config.GAUSSIAN_BLUR_KERNEL)

            processing_events.append(make_processing_event(record_dict, "segmentation", "method", config.SEGMENTATION_METHOD, "success", "OK", "Otsu threshold applied"))
            processing_events.append(make_processing_event(record_dict, "segmentation", "foreground", foreground, "success", "OK", "Foreground direction recorded"))
            mask = segment_root_otsu(preprocessed, foreground=foreground)

            processing_events.append(make_processing_event(record_dict, "mask_cleaning", "min_object_size_px", config.MIN_OBJECT_SIZE_PX, "success", "OK", "Small objects removed"))
            processing_events.append(make_processing_event(record_dict, "mask_cleaning", "fill_holes", config.FILL_HOLES, "success", "OK", "Hole filling parameter recorded"))
            cleaned_mask = clean_mask(
                mask,
                min_object_size_px=config.MIN_OBJECT_SIZE_PX,
                remove_small=config.REMOVE_SMALL_OBJECTS,
                fill_holes=config.FILL_HOLES,
            )

            skeleton = skeletonize_mask(cleaned_mask)
            processing_events.append(make_processing_event(record_dict, "skeletonization", "method", "skimage.skeletonize", "success", "OK", "Skeleton created"))

            processing_events.append(make_processing_event(record_dict, "mask_quality", "max_mask_area_fraction", config.MAX_MASK_AREA_FRACTION, "success", "OK", "Maximum allowed mask area fraction recorded"))
            features = extract_morphological_features(cleaned_mask, skeleton)
            processing_events.append(make_processing_event(record_dict, "mask_quality", "mask_area_fraction", features["mask_area_fraction"], features["processing_status"], features["reason"], features["message"]))
            row = {
                "record_id": record["record_id"],
                "image_id": record["image_id"],
                "image_name": record["image_name_clean"],
                "sample_id": record["sample_id_clean"],
                "roi_used": False,
                **features,
            }
            measurements.append(row)

            processing_events.append(make_processing_event(record_dict, "feature_extraction", "area_source", "segmentation_mask", features["processing_status"], features["reason"], features["message"]))

            if features["processing_status"] != "failed":
                image_id = record["image_id"]
                save_mask(cleaned_mask, masks_dir / f"{image_id}_mask.png")
                save_skeleton(skeleton, skeletons_dir / f"{image_id}_skeleton.png")
                save_overlay(image, cleaned_mask, skeleton, overlays_dir / f"{image_id}_overlay.png")
                processing_events.append(make_processing_event(record_dict, "export_images", "outputs", image_id, "success", "OK", "Mask, skeleton and overlay exported"))

        except Exception as exc:
            message = str(exc)
            measurements.append(_failed_measurement(record_dict, "UNKNOWN_ERROR", message))
            processing_events.append(make_processing_event(record_dict, "analysis", "exception", message, "failed", "UNKNOWN_ERROR", message))

    summary_metadata = {
        "manifest_records": len(manifest),
        "records_selected_for_analysis": len(valid_records),
        "records_skipped_not_valid": len(manifest) - len(valid_records),
    }
    paths = export_analysis_outputs(
        measurements,
        processing_events,
        output,
        summary_metadata=summary_metadata,
    )
    return measurements, processing_events, paths
