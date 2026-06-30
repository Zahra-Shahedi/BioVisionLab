
from pathlib import Path
import json
import cv2

from plate_analysis.pipeline import get_analysis_settings


def create_config_preview(image_path, config_path, output_path):
    """
    Create a preview image showing how BioVisionLab interprets one plate image.

    The preview shows:
    - analysis plate circle
    - left/right split line
    - estimated left plug position
    - estimated right plug position
    """

    image_path = Path(image_path)
    config_path = Path(config_path)
    output_path = Path(output_path)

    img = cv2.imread(str(image_path))

    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    with open(config_path, "r") as file:
        config = json.load(file)

    settings = get_analysis_settings(image_path, config)

    if settings is None:
        raise ValueError("Could not detect Petri dish using this config.")

    preview = img.copy()

    center_x, center_y = settings["plate_center"]
    radius = settings["plate_radius"]
    split_x = settings["split_x"]
    left_start = settings["left_start"]
    right_start = settings["right_start"]

    image_height, image_width = preview.shape[:2]

    # Analysis circle
    cv2.circle(
        preview,
        (center_x, center_y),
        radius,
        (255, 0, 255),
        3
    )

    # Split line
    cv2.line(
        preview,
        (split_x, 0),
        (split_x, image_height),
        (255, 255, 0),
        2
    )

    # Left plug position
    cv2.circle(
        preview,
        left_start,
        12,
        (0, 0, 255),
        -1
    )

    cv2.putText(
        preview,
        "Left plug",
        (left_start[0] + 15, left_start[1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
        cv2.LINE_AA
    )

    # Right plug position
    cv2.circle(
        preview,
        right_start,
        12,
        (0, 255, 0),
        -1
    )

    cv2.putText(
        preview,
        "Right plug",
        (right_start[0] + 15, right_start[1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
        cv2.LINE_AA
    )

    # Plate center
    cv2.circle(
        preview,
        (center_x, center_y),
        8,
        (255, 255, 255),
        -1
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), preview)

    return {
        "output_path": output_path,
        "plate_center": (center_x, center_y),
        "plate_radius": radius,
        "split_x": split_x,
        "left_start": left_start,
        "right_start": right_start
    }
