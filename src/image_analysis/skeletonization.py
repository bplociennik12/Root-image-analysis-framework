import numpy as np
from skimage.morphology import skeletonize


def skeletonize_mask(mask: np.ndarray) -> np.ndarray:
    return skeletonize(mask.astype(bool))
