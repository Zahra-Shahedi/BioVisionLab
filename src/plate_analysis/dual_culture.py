
from pathlib import Path
import cv2
import numpy as np


def _make_fungus_mask(
    gray,
    plate_mask,
    threshold=220,
    threshold_method="global",
    adaptive_block_size=51,
    adaptive_c=2
):
    """
    Create fungal colony mask from grayscale image.

    threshold_method options:
    - global: gray > threshold
    - otsu: automatic global threshold
    - adaptive: local thresholding for uneven lighting
    """

    threshold_method = str(threshold_method).lower()

    if threshold_method == "global":
        fungus_mask = gray > threshold

    elif threshold_method == "otsu":
        plate_pixels = gray[plate_mask > 0]

        if len(plate_pixels) == 0:
            fungus_mask = np.zeros_like(gray, dtype=bool)
        else:
            otsu_threshold, _ = cv2.threshold(
                plate_pixels,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            fungus_mask = gray > otsu_threshold

    elif threshold_method == "adaptive":
        if adaptive_block_size % 2 == 0:
            adaptive_block_size += 1

        if adaptive_block_size < 3:
            adaptive_block_size = 3

        adaptive = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            adaptive_block_size,
            adaptive_c
        )

        fungus_mask = adaptive > 0

    else:
        raise ValueError(
            "threshold_method must be one of: global, otsu, adaptive"
        )

    fungus_mask = fungus_mask & (plate_mask > 0)

    return fungus_mask.astype(np.uint8) * 255


def _largest_contour(binary_mask):
    """
    Return largest contour from a binary mask.
    """

    contours, _ = cv2.findContours(
        binary_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if len(contours) == 0:
        return None

    return max(contours, key=cv2.contourArea)


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
    annotated_dir=None,
    threshold_method="global",
    adaptive_block_size=51,
    adaptive_c=2
):
    """
    Analyze one dual-culture Petri dish image.

    Measures:
    - left colony width
    - right colony width
    - left/right growth toward the opposing colony
    - gap between colonies
    """

    image_path = Path(image_path)

    img = cv2.imread(str(image_path))

    if img is None:
        return {
            "image": image_path.name,
            "detected": False,
            "failure_reason": "Image could not be read"
        }

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    plate_mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.circle(
        plate_mask,
        tuple(plate_center),
        int(plate_radius),
        255,
        -1
    )

    fungus_mask = _make_fungus_mask(
        gray=gray,
        plate_mask=plate_mask,
        threshold=threshold,
        threshold_method=threshold_method,
        adaptive_block_size=adaptive_block_size,
        adaptive_c=adaptive_c
    )

    left_region = np.zeros(gray.shape, dtype=np.uint8)
    left_region[:, :int(split_x)] = 255

    right_region = np.zeros(gray.shape, dtype=np.uint8)
    right_region[:, int(split_x):] = 255

    left_mask = cv2.bitwise_and(fungus_mask, left_region)
    right_mask = cv2.bitwise_and(fungus_mask, right_region)

    left_contour = _largest_contour(left_mask)
    right_contour = _largest_contour(right_mask)

    if left_contour is None or right_contour is None:
        return {
            "image": image_path.name,
            "detected": False,
            "failure_reason": "One or both colonies not detected",
            "threshold_method": threshold_method
        }

    left_x, left_y, left_w, left_h = cv2.boundingRect(left_contour)
    right_x, right_y, right_w, right_h = cv2.boundingRect(right_contour)

    left_edge_toward = left_x + left_w
    right_edge_toward = right_x

    gap_px = right_edge_toward - left_edge_toward

    left_growth_toward_px = left_edge_toward - left_start[0]
    right_growth_toward_px = right_start[0] - right_edge_toward

    result = {
        "image": image_path.name,
        "detected": True,
        "failure_reason": "",
        "threshold_method": threshold_method,
        "left_width_mm": left_w / pixels_per_mm,
        "left_height_mm": left_h / pixels_per_mm,
        "right_width_mm": right_w / pixels_per_mm,
        "right_height_mm": right_h / pixels_per_mm,
        "left_growth_toward_mm": left_growth_toward_px / pixels_per_mm,
        "right_growth_toward_mm": right_growth_toward_px / pixels_per_mm,
        "gap_mm": gap_px / pixels_per_mm,
        "left_area_px": cv2.contourArea(left_contour),
        "right_area_px": cv2.contourArea(right_contour)
    }

    if save_annotated:
        if annotated_dir is None:
            annotated_dir = image_path.parent / "annotated"

        annotated_dir = Path(annotated_dir)
        annotated_dir.mkdir(parents=True, exist_ok=True)

        annotated = img.copy()

        cv2.drawContours(annotated, [left_contour], -1, (0, 0, 255), 2)
        cv2.drawContours(annotated, [right_contour], -1, (0, 255, 0), 2)

        cv2.rectangle(
            annotated,
            (left_x, left_y),
            (left_x + left_w, left_y + left_h),
            (0, 0, 255),
            2
        )

        cv2.rectangle(
            annotated,
            (right_x, right_y),
            (right_x + right_w, right_y + right_h),
            (0, 255, 0),
            2
        )

        cv2.line(
            annotated,
            (left_edge_toward, plate_center[1]),
            (right_edge_toward, plate_center[1]),
            (255, 0, 0),
            3
        )

        cv2.circle(annotated, tuple(left_start), 6, (0, 0, 255), -1)
        cv2.circle(annotated, tuple(right_start), 6, (0, 255, 0), -1)

        label = f"gap={result['gap_mm']:.2f} mm | {threshold_method}"
        cv2.putText(
            annotated,
            label,
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        annotated_path = annotated_dir / f"{image_path.stem}_annotated.png"
        cv2.imwrite(str(annotated_path), annotated)

    return result
