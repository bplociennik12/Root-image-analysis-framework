from pathlib import Path
import cv2
import numpy as np


def save_mask(mask: np.ndarray, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), (mask.astype(np.uint8) * 255))


def save_skeleton(skeleton: np.ndarray, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), (skeleton.astype(np.uint8) * 255))


def save_overlay(image: np.ndarray, mask: np.ndarray, skeleton: np.ndarray, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    overlay = image.copy()
    if overlay.ndim == 2:
        overlay = cv2.cvtColor(overlay, cv2.COLOR_GRAY2BGR)

    overlay[mask.astype(bool)] = [0, 255, 0]
    overlay[skeleton.astype(bool)] = [0, 0, 255]
    cv2.imwrite(str(path), overlay)
