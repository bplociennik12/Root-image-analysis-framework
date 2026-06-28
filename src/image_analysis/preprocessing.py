import cv2
import numpy as np


def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def apply_gaussian_blur(gray: np.ndarray, kernel_size: int) -> np.ndarray:
    if kernel_size % 2 == 0:
        raise ValueError("Gaussian blur kernel size must be odd.")
    return cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)


def preprocess_image(image: np.ndarray, kernel_size: int) -> np.ndarray:
    gray = convert_to_grayscale(image)
    return apply_gaussian_blur(gray, kernel_size)
