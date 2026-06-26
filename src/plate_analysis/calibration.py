
from pathlib import Path
import cv2
import numpy as np


def detect_petri_dish(image_path):
    """
    Detect the Petri dish circle in an image.

    Returns:
    - center_x
    - center_y
    - radius_pixels
    - diameter_pixels
    """

    image_path = Path(image_path)
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Blur helps remove tiny pixel noise before circle detection
    blurred = cv2.medianBlur(gray, 5)

    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=100,
        param1=50,
        param2=30,
        minRadius=150,
        maxRadius=300
    )

    if circles is None:
        return None

    circles = np.round(circles[0, :]).astype("int")

    # Choose the largest detected circle
    largest_circle = max(circles, key=lambda c: c[2])

    center_x, center_y, radius = largest_circle

    return {
        "center_x": center_x,
        "center_y": center_y,
        "radius_pixels": radius,
        "diameter_pixels": radius * 2
    }
