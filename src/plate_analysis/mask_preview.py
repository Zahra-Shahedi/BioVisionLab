
from pathlib import Path
import json
import cv2
import numpy as np

from plate_analysis.pipeline import get_analysis_settings
from plate_analysis.dual_culture import _make_fungus_mask


def create_mask_preview(
    image_path,
    config_path,
    output_dir
):
    """
    Create mask preview outputs for one image.

    Outputs:
    - grayscale image
    - binary fungus mask
    - overlay image showing mask on original image
    """

    image_path = Path(image_path)
    config_path = Path(config_path)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    img = cv2.imread(str(image_path))

    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    with open(config_path, "r") as file:
        config = json.load(file)

    settings = get_analysis_settings(image_path, config)

    if settings is None:
        raise ValueError("Could not detect/apply plate settings for this image.")

    plate_mask = np.zeros(gray.shape, dtype=np.uint8)

    cv2.circle(
        plate_mask,
        tuple(settings["plate_center"]),
        int(settings["plate_radius"]),
        255,
        -1
    )

    fungus_mask = _make_fungus_mask(
        gray=gray,
        plate_mask=plate_mask,
        threshold=config.get("threshold", 220),
        threshold_method=config.get("threshold_method", "global"),
        adaptive_block_size=config.get("adaptive_block_size", 51),
        adaptive_c=config.get("adaptive_c", 2),
        open_kernel_size=config.get("open_kernel_size", 0),
        close_kernel_size=config.get("close_kernel_size", 0)
    )

    overlay = img.copy()

    red_layer = np.zeros_like(img)
    red_layer[:, :, 2] = 255

    mask_bool = fungus_mask > 0
    overlay[mask_bool] = cv2.addWeighted(
        overlay[mask_bool],
        0.55,
        red_layer[mask_bool],
        0.45,
        0
    )

    stem = image_path.stem

    gray_path = output_dir / f"{stem}_gray.png"
    mask_path = output_dir / f"{stem}_fungus_mask.png"
    overlay_path = output_dir / f"{stem}_mask_overlay.png"

    cv2.imwrite(str(gray_path), gray)
    cv2.imwrite(str(mask_path), fungus_mask)
    cv2.imwrite(str(overlay_path), overlay)

    mask_area_px = int((fungus_mask > 0).sum())

    return {
        "gray_path": gray_path,
        "mask_path": mask_path,
        "overlay_path": overlay_path,
        "mask_area_px": mask_area_px,
        "threshold_method": config.get("threshold_method", "global")
    }
