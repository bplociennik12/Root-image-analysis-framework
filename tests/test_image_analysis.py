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
