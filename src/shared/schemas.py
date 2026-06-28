REQUIRED_RAW_METADATA_COLUMNS = ["image_name", "sample_id"]

OPTIONAL_METADATA_COLUMNS = ["species", "treatment", "replicate", "notes"]

CLEAN_MANIFEST_COLUMNS = [
    "record_id",
    "image_id",
    "image_name_original",
    "image_name_clean",
    "image_path",
    "sample_id_original",
    "sample_id_clean",
    "file_format",
    "width_px",
    "height_px",
    "is_valid",
    "record_status",
    "reason",
    "message",
    "audit_events_count",
]

REJECTED_RECORDS_COLUMNS = [
    "record_id",
    "image_id",
    "image_name_original",
    "image_name_clean",
    "image_path",
    "sample_id_original",
    "sample_id_clean",
    "record_status",
    "reason",
    "message",
]

AUDIT_LOG_COLUMNS = [
    "timestamp",
    "record_id",
    "image_id",
    "image_name",
    "sample_id",
    "step",
    "rule_id",
    "rule_description",
    "input_value",
    "output_value",
    "action",
    "status",
    "reason",
    "message",
]

ROOT_MEASUREMENTS_COLUMNS = [
    "record_id",
    "image_id",
    "image_name",
    "sample_id",
    "roi_used",
    "area_px",
    "skeleton_length_px",
    "branch_points_count",
    "endpoints_count",
    "bbox_width_px",
    "bbox_height_px",
    "aspect_ratio",
    "centroid_x_px",
    "centroid_y_px",
    "component_count",
    "processing_status",
    "reason",
    "message",
]

PROCESSING_LOG_COLUMNS = [
    "timestamp",
    "record_id",
    "image_id",
    "image_name",
    "step",
    "parameter",
    "value",
    "status",
    "reason",
    "message",
]
