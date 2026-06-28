import numpy as np
from scipy.ndimage import convolve

KERNEL_8_NEIGHBORS = np.array(
    [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ],
    dtype=np.uint8,
)


def count_skeleton_length(skeleton: np.ndarray) -> int:
    return int(np.count_nonzero(skeleton))


def count_endpoints(skeleton: np.ndarray) -> int:
    skel = skeleton.astype(bool)
    neighbors = convolve(skel.astype(np.uint8), KERNEL_8_NEIGHBORS, mode="constant", cval=0)
    return int(np.count_nonzero(skel & (neighbors == 1)))


def count_branch_points(skeleton: np.ndarray) -> int:
    skel = skeleton.astype(bool)
    neighbors = convolve(skel.astype(np.uint8), KERNEL_8_NEIGHBORS, mode="constant", cval=0)
    return int(np.count_nonzero(skel & (neighbors >= 3)))
