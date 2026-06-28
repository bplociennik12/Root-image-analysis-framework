from pathlib import Path
import cv2


def load_image(image_path: str | Path):
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Image could not be loaded: {image_path}")
    return image
