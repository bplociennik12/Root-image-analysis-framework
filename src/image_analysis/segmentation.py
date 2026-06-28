import cv2
import numpy as np
from scipy import ndimage as ndi
from skimage.measure import label


def segment_root_otsu(gray_blurred: np.ndarray, foreground: str = "dark") -> np.ndarray:
    threshold_value, binary = cv2.threshold(
        gray_blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    if foreground == "dark":
        mask = binary == 0
    elif foreground == "light":
        mask = binary > 0
    else:
        raise ValueError("foreground must be 'dark' or 'light'.")

    return mask.astype(bool)


def _remove_small_components(mask: np.ndarray, min_object_size_px: int) -> np.ndarray:
    labeled = label(mask.astype(bool))
    if labeled.max() == 0:
        return mask.astype(bool)

    cleaned = np.zeros_like(mask, dtype=bool)
    for component_id in range(1, int(labeled.max()) + 1):
        component = labeled == component_id
        if int(np.count_nonzero(component)) >= min_object_size_px:
            cleaned |= component
    return cleaned


def clean_mask(
    mask: np.ndarray,
    min_object_size_px: int,
    remove_small: bool = True,
    fill_holes: bool = True,
) -> np.ndarray:
    cleaned = mask.astype(bool)
    if remove_small:
        cleaned = _remove_small_components(cleaned, min_object_size_px)
    if fill_holes:
        cleaned = ndi.binary_fill_holes(cleaned)
    return cleaned.astype(bool)
