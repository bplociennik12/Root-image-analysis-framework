import numpy as np

from image_analysis import config
from skimage.measure import label, regionprops

from image_analysis.skeleton_features import (
    count_branch_points,
    count_endpoints,
    count_skeleton_length,
)


def extract_morphological_features(
    mask: np.ndarray,
    skeleton: np.ndarray,
    max_mask_area_fraction: float = config.MAX_MASK_AREA_FRACTION,
) -> dict:
    mask_bool = mask.astype(bool)
    labeled = label(mask_bool)
    component_count = int(labeled.max())

    if component_count == 0:
        return {
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
            "mask_area_fraction": 0.0,
            "processing_status": "failed",
            "reason": "EMPTY_MASK",
            "message": "Segmentation produced an empty mask.",
        }

    props = regionprops(labeled)
    all_coords = np.argwhere(mask_bool)
    min_row, min_col = all_coords.min(axis=0)
    max_row, max_col = all_coords.max(axis=0)
    bbox_height = int(max_row - min_row + 1)
    bbox_width = int(max_col - min_col + 1)

    centroid_y, centroid_x = all_coords.mean(axis=0)
    aspect_ratio = float(bbox_width / bbox_height) if bbox_height else 0.0

    area_px = int(np.count_nonzero(mask_bool))
    mask_area_fraction = area_px / mask_bool.size if mask_bool.size else 0.0

    if mask_area_fraction > max_mask_area_fraction:
        status = "warning"
        reason = "MASK_TOO_LARGE"
        message = "Segmentation mask covers too much of the image."
    elif component_count > 1:
        status = "warning"
        reason = "MULTIPLE_COMPONENTS"
        message = "Multiple mask components detected; full cleaned mask was analyzed."
    else:
        status = "success"
        reason = "OK"
        message = "Features extracted successfully."

    return {
        "area_px": area_px,
        "skeleton_length_px": count_skeleton_length(skeleton),
        "branch_points_count": count_branch_points(skeleton),
        "endpoints_count": count_endpoints(skeleton),
        "bbox_width_px": bbox_width,
        "bbox_height_px": bbox_height,
        "aspect_ratio": aspect_ratio,
        "centroid_x_px": float(centroid_x),
        "centroid_y_px": float(centroid_y),
        "component_count": component_count,
        "mask_area_fraction": float(mask_area_fraction),
        "processing_status": status,
        "reason": reason,
        "message": message,
    }
