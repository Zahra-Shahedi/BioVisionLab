
from pathlib import Path
import cv2
import numpy as np


def analyze_dual_culture_image(
    image_path,
    pixels_per_mm,
    threshold=220,
    plate_center=(300, 300),
    plate_radius=225,
    split_x=300,
    left_start=(210, 300),
    right_start=(390, 300),
    save_annotated=False,
    annotated_dir=None
):
    """
    Analyze one dual-culture Petri dish image.

    Measures:
    - left colony width/height
    - right colony width/height
    - growth toward the opposite colony
    - gap between colonies
    """

    image_path = Path(image_path)

    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    yy, xx = np.ogrid[:gray.shape[0], :gray.shape[1]]
    distance = np.sqrt((xx - plate_center[0])**2 + (yy - plate_center[1])**2)
    plate_mask = distance < plate_radius

    fungus_mask = ((gray > threshold) & plate_mask).astype("uint8") * 255

    left_mask = fungus_mask.copy()
    left_mask[:, split_x:] = 0

    right_mask = fungus_mask.copy()
    right_mask[:, :split_x] = 0

    contours_left, _ = cv2.findContours(
        left_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    contours_right, _ = cv2.findContours(
        right_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    result = {
        "image": image_path.name,
        "detected": False
    }

    if len(contours_left) == 0 or len(contours_right) == 0:
        return result

    left_colony = max(contours_left, key=cv2.contourArea)
    right_colony = max(contours_right, key=cv2.contourArea)

    xL, yL, wL, hL = cv2.boundingRect(left_colony)
    xR, yR, wR, hR = cv2.boundingRect(right_colony)

    left_right_edge = xL + wL
    right_left_edge = xR

    gap_px = right_left_edge - left_right_edge

    left_growth_toward_px = left_right_edge - left_start[0]
    right_growth_toward_px = right_start[0] - right_left_edge

    result = {
        "image": image_path.name,
        "detected": True,

        "left_width_mm": wL / pixels_per_mm,
        "left_height_mm": hL / pixels_per_mm,
        "right_width_mm": wR / pixels_per_mm,
        "right_height_mm": hR / pixels_per_mm,

        "left_growth_toward_mm": left_growth_toward_px / pixels_per_mm,
        "right_growth_toward_mm": right_growth_toward_px / pixels_per_mm,
        "gap_mm": gap_px / pixels_per_mm,

        "left_area_px": cv2.contourArea(left_colony),
        "right_area_px": cv2.contourArea(right_colony)
    }

    if save_annotated:
        if annotated_dir is None:
            raise ValueError("annotated_dir must be provided if save_annotated=True")

        annotated_dir = Path(annotated_dir)
        annotated_dir.mkdir(parents=True, exist_ok=True)

        annotated = image_rgb.copy()

        cv2.drawContours(annotated, [left_colony], -1, (255, 0, 0), 3)
        cv2.drawContours(annotated, [right_colony], -1, (0, 255, 0), 3)

        cv2.rectangle(annotated, (xL, yL), (xL + wL, yL + hL), (255, 0, 0), 2)
        cv2.rectangle(annotated, (xR, yR), (xR + wR, yR + hR), (0, 255, 0), 2)

        cv2.line(
            annotated,
            (left_right_edge, plate_center[1]),
            (right_left_edge, plate_center[1]),
            (255, 255, 0),
            3
        )

        cv2.putText(
            annotated,
            f"Gap: {gap_px / pixels_per_mm:.1f} mm",
            (230, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        output_path = annotated_dir / image_path.name
        cv2.imwrite(str(output_path), cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))

    return result
