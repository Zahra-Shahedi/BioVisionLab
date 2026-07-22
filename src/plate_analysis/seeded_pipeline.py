
from pathlib import Path
import json
import cv2
import numpy as np
import pandas as pd

from plate_analysis.metadata import parse_plate_metadata
from plate_analysis.seeded_segmentation import make_seeded_colony_mask


def _largest_contour(mask, min_area_px=200):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    contours = [c for c in contours if cv2.contourArea(c) >= min_area_px]

    if not contours:
        return None

    return max(contours, key=cv2.contourArea)


def _apply_image_calibration(config, image_name, calibration_table=None):
    """
    Override seed/agar/split coordinates for one image using a calibration table.
    """

    config = config.copy()

    if calibration_table is None:
        return config

    matches = calibration_table[calibration_table["image_name"] == image_name]

    if matches.empty:
        return config

    row = matches.iloc[0]

    coordinate_keys = [
        "left_start_x",
        "left_start_y",
        "right_start_x",
        "right_start_y",
        "agar_reference_x",
        "agar_reference_y",
        "split_x",
        "colony_search_radius",
        "seed_radius",
        "agar_radius",
        "gray_offset",
        "contrast_offset",
        "min_colony_area_px",
        "plate_center_x",
        "plate_center_y",
        "plate_radius_pixels",
        "inner_plate_radius_factor",
    ]

    int_keys = [
        "left_start_x",
        "left_start_y",
        "right_start_x",
        "right_start_y",
        "agar_reference_x",
        "agar_reference_y",
        "split_x",
        "colony_search_radius",
        "seed_radius",
        "agar_radius",
        "min_colony_area_px",
        "plate_center_x",
        "plate_center_y",
        "plate_radius_pixels",
    ]

    float_keys = [
        "gray_offset",
        "contrast_offset",
        "inner_plate_radius_factor",
    ]

    for key in coordinate_keys:
        if key in row and not pd.isna(row[key]):
            if key in int_keys:
                config[key] = int(row[key])
            elif key in float_keys:
                config[key] = float(row[key])
            else:
                config[key] = row[key]

    return config


def analyze_seeded_dual_culture_image(image_path, config, annotated_dir=None):
    image_path = Path(image_path)

    img = cv2.imread(str(image_path))

    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    plate_diameter_mm = config["plate_diameter_mm"]
    plate_radius_pixels = config["plate_radius_pixels"]
    pixels_per_mm = (plate_radius_pixels * 2) / plate_diameter_mm

    left_center = (config["left_start_x"], config["left_start_y"])
    right_center = (config["right_start_x"], config["right_start_y"])
    agar_center = (config["agar_reference_x"], config["agar_reference_y"])

    mask = make_seeded_colony_mask(
        gray=gray,
        left_center=left_center,
        right_center=right_center,
        agar_center=agar_center,
        colony_search_radius=config.get("colony_search_radius", 190),
        seed_radius=config.get("seed_radius", 35),
        agar_radius=config.get("agar_radius", 90),
        gray_offset=config.get("gray_offset", 8),
        contrast_offset=config.get("contrast_offset", 2),
        background_blur_size=config.get("background_blur_size", 151),
        open_kernel_size=config.get("open_kernel_size", 3),
        close_kernel_size=config.get("close_kernel_size", 9),
        min_area_px=config.get("min_colony_area_px", 200),
        plate_center=(
            config.get("plate_center_x"),
            config.get("plate_center_y")
        ) if "plate_center_x" in config and "plate_center_y" in config else None,
        plate_radius=config.get("plate_radius_pixels"),
        inner_plate_radius_factor=config.get("inner_plate_radius_factor", 0.88)
    )

    split_x = config["split_x"]

    left_mask = np.zeros_like(mask)
    right_mask = np.zeros_like(mask)

    left_mask[:, :split_x] = mask[:, :split_x]
    right_mask[:, split_x:] = mask[:, split_x:]

    left_contour = _largest_contour(left_mask, min_area_px=config.get("min_colony_area_px", 200))
    right_contour = _largest_contour(right_mask, min_area_px=config.get("min_colony_area_px", 200))

    result = {
        "image_name": image_path.name,
        "image_path": str(image_path),
        "detected": False,
        "failure_reason": "",
    }

    result.update(parse_plate_metadata(image_path.name))

    if left_contour is None or right_contour is None:
        result["failure_reason"] = "Could not detect both colonies"
        return result

    lx, ly, lw, lh = cv2.boundingRect(left_contour)
    rx, ry, rw, rh = cv2.boundingRect(right_contour)

    left_right_edge = lx + lw
    right_left_edge = rx
    gap_pixels = right_left_edge - left_right_edge

    left_growth_toward_px = left_right_edge - left_center[0]
    right_growth_toward_px = right_center[0] - right_left_edge

    result.update({
        "detected": True,
        "left_width_mm": lw / pixels_per_mm,
        "left_height_mm": lh / pixels_per_mm,
        "right_width_mm": rw / pixels_per_mm,
        "right_height_mm": rh / pixels_per_mm,
        "gap_mm": gap_pixels / pixels_per_mm,
        "left_growth_toward_mm": left_growth_toward_px / pixels_per_mm,
        "right_growth_toward_mm": right_growth_toward_px / pixels_per_mm,
        "left_bbox_x": lx,
        "left_bbox_y": ly,
        "left_bbox_width_px": lw,
        "left_bbox_height_px": lh,
        "right_bbox_x": rx,
        "right_bbox_y": ry,
        "right_bbox_width_px": rw,
        "right_bbox_height_px": rh,
        "left_area_px": int(cv2.contourArea(left_contour)),
        "right_area_px": int(cv2.contourArea(right_contour)),
        "pixels_per_mm": pixels_per_mm,
        "left_start_x": left_center[0],
        "left_start_y": left_center[1],
        "right_start_x": right_center[0],
        "right_start_y": right_center[1],
        "agar_reference_x": agar_center[0],
        "agar_reference_y": agar_center[1],
        "split_x": split_x,
    })

    if annotated_dir is not None:
        annotated_dir = Path(annotated_dir)
        annotated_dir.mkdir(parents=True, exist_ok=True)

        annotated = img.copy()

        overlay = annotated.copy()
        overlay[mask > 0] = (
            0.55 * overlay[mask > 0] + 0.45 * np.array([0, 0, 255])
        ).astype(np.uint8)

        annotated = overlay

        cv2.rectangle(annotated, (lx, ly), (lx + lw, ly + lh), (0, 255, 0), 3)
        cv2.rectangle(annotated, (rx, ry), (rx + rw, ry + rh), (0, 255, 0), 3)

        cv2.circle(annotated, left_center, config.get("seed_radius", 35), (255, 0, 0), 3)
        cv2.circle(annotated, right_center, config.get("seed_radius", 35), (255, 0, 0), 3)
        cv2.circle(annotated, agar_center, config.get("agar_radius", 90), (0, 255, 255), 3)

        out_path = annotated_dir / f"{image_path.stem}_seeded_annotated.png"
        cv2.imwrite(str(out_path), annotated)

        result["annotated_path"] = str(out_path)

    return result


def analyze_seeded_folder(input_dir, config_path, output_csv, annotated_dir, calibration_csv=None):
    input_dir = Path(input_dir)
    config_path = Path(config_path)
    output_csv = Path(output_csv)
    annotated_dir = Path(annotated_dir)

    with open(config_path, "r") as file:
        base_config = json.load(file)

    calibration_table = None

    if calibration_csv is not None:
        calibration_csv = Path(calibration_csv)
        calibration_table = pd.read_csv(calibration_csv)

    image_paths = sorted(
        list(input_dir.glob("*.png")) +
        list(input_dir.glob("*.jpg")) +
        list(input_dir.glob("*.jpeg"))
    )

    results = []

    for image_path in image_paths:
        try:
            config = _apply_image_calibration(
                config=base_config,
                image_name=image_path.name,
                calibration_table=calibration_table
            )

            result = analyze_seeded_dual_culture_image(
                image_path=image_path,
                config=config,
                annotated_dir=annotated_dir
            )
        except Exception as error:
            result = {
                "image_name": image_path.name,
                "image_path": str(image_path),
                "detected": False,
                "failure_reason": str(error)
            }

        results.append(result)

    output_csv.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)

    return df
