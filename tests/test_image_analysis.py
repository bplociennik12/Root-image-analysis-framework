import numpy as np

from image_analysis.segmentation import clean_mask
from image_analysis.skeletonization import skeletonize_mask
from image_analysis.morphology import extract_morphological_features
from image_analysis.skeleton_features import count_endpoints, count_skeleton_length


def test_skeleton_features_on_simple_line():
    skeleton = np.zeros((5, 5), dtype=bool)
    skeleton[2, 1:4] = True

    assert count_skeleton_length(skeleton) == 3
    assert count_endpoints(skeleton) == 2


def test_extract_morphological_features_success():
    mask = np.zeros((10, 10), dtype=bool)
    mask[2:8, 4:6] = True
    skeleton = skeletonize_mask(mask)

    features = extract_morphological_features(mask, skeleton)

    assert features["area_px"] == 12
    assert features["component_count"] == 1
    assert features["processing_status"] == "success"


def test_empty_mask_returns_failed_status():
    mask = np.zeros((10, 10), dtype=bool)
    skeleton = skeletonize_mask(mask)

    features = extract_morphological_features(mask, skeleton)

    assert features["processing_status"] == "failed"
    assert features["reason"] == "EMPTY_MASK"


def test_multiple_components_returns_warning():
    mask = np.zeros((20, 20), dtype=bool)
    mask[2:6, 2:6] = True
    mask[12:16, 12:16] = True
    skeleton = skeletonize_mask(mask)

    features = extract_morphological_features(mask, skeleton)

    assert features["component_count"] == 2
    assert features["processing_status"] == "warning"
    assert features["reason"] == "MULTIPLE_COMPONENTS"

def test_extract_morphological_features_warns_when_mask_is_too_large():
    import numpy as np

    from image_analysis.morphology import extract_morphological_features

    mask = np.ones((10, 10), dtype=bool)
    skeleton = np.zeros((10, 10), dtype=bool)

    features = extract_morphological_features(
        mask,
        skeleton,
        max_mask_area_fraction=0.60,
    )

    assert features["area_px"] == 100
    assert features["processing_status"] == "warning"
    assert features["reason"] == "MASK_TOO_LARGE"
    assert features["message"] == "Segmentation mask covers too much of the image."

def test_analysis_pipeline_logs_max_mask_area_fraction(tmp_path):
    import cv2
    import pandas as pd

    from image_analysis.pipeline import run_analysis_pipeline

    image_path = tmp_path / "root.png"
    manifest_path = tmp_path / "clean_manifest.csv"
    output_dir = tmp_path / "analysis"

    image = np.ones((40, 40, 3), dtype=np.uint8) * 255
    cv2.line(image, (20, 5), (20, 35), (0, 0, 0), 2)
    cv2.imwrite(str(image_path), image)

    manifest = pd.DataFrame(
        [
            {
                "record_id": 0,
                "image_id": "IMG_TEST",
                "image_name_original": "root.png",
                "image_name_clean": "root.png",
                "image_path": str(image_path),
                "sample_id_original": "S001",
                "sample_id_clean": "S001",
                "file_format": "png",
                "width_px": 40,
                "height_px": 40,
                "is_valid": True,
                "record_status": "valid",
                "reason": "OK",
                "message": "Record is ready for analysis",
                "audit_events_count": 0,
            }
        ]
    )
    manifest.to_csv(manifest_path, index=False)

    _, _, paths = run_analysis_pipeline(
        manifest_path,
        output_dir,
        foreground="dark",
    )

    processing_log = pd.read_csv(paths["processing_log"])

    matching_rows = processing_log[
        (processing_log["step"] == "mask_quality")
        & (processing_log["parameter"] == "max_mask_area_fraction")
    ]

    assert len(matching_rows) == 1
    assert float(matching_rows.iloc[0]["value"]) == 0.6
    assert matching_rows.iloc[0]["status"] == "success"
    assert matching_rows.iloc[0]["reason"] == "OK"

    area_fraction_rows = processing_log[
        (processing_log["step"] == "mask_quality")
        & (processing_log["parameter"] == "mask_area_fraction")
    ]

    assert len(area_fraction_rows) == 1
    mask_area_fraction = float(area_fraction_rows.iloc[0]["value"])
    assert 0.0 <= mask_area_fraction <= 1.0
    assert area_fraction_rows.iloc[0]["status"] in {"success", "warning", "failed"}
    assert area_fraction_rows.iloc[0]["reason"] in {"OK", "MULTIPLE_COMPONENTS", "MASK_TOO_LARGE", "EMPTY_MASK"}

def test_export_analysis_summary_counts_mask_too_large(tmp_path):
    import pandas as pd

    from image_analysis.csv_exporter import export_analysis_outputs

    measurements = [
        {
            "record_id": 0,
            "image_id": "IMG_001",
            "image_name": "root_001.png",
            "sample_id": "S001",
            "roi_used": False,
            "area_px": 100,
            "skeleton_length_px": 20,
            "branch_points_count": 0,
            "endpoints_count": 2,
            "bbox_width_px": 10,
            "bbox_height_px": 20,
            "aspect_ratio": 0.5,
            "centroid_x_px": 5,
            "centroid_y_px": 10,
            "component_count": 1,
            "processing_status": "warning",
            "reason": "MASK_TOO_LARGE",
            "message": "Segmentation mask covers too much of the image.",
        }
    ]

    paths = export_analysis_outputs(
        measurements=measurements,
        processing_events=[],
        output_dir=tmp_path,
    )

    summary = pd.read_csv(paths["analysis_summary"])
    summary_values = dict(zip(summary["metric"], summary["value"]))

    assert summary_values["mask_too_large"] == 1
    assert summary_values["analysis_warning"] == 1
