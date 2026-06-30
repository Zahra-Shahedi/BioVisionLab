
from pathlib import Path
import json
import shutil
import pandas as pd

from plate_analysis.dual_culture import analyze_dual_culture_image
from plate_analysis.metadata import parse_plate_metadata
from plate_analysis.plotting import plot_dual_culture_summary
from plate_analysis.reporting import create_dual_culture_report
from plate_analysis.calibration import detect_petri_dish


def get_analysis_settings(image_path, config):
    """
    Decide plate center, radius, split line, and pixels/mm for one image.

    Supports:
    - fixed plate settings
    - automatic Petri dish detection
    """

    plate_diameter_mm = config["plate_diameter_mm"]

    if config["plate_radius_pixels"] == "auto":
        dish = detect_petri_dish(image_path)

        if dish is None:
            return None

        center_x = dish["center_x"]
        center_y = dish["center_y"]
        detected_radius = dish["radius_pixels"]

        analysis_radius = int(detected_radius * 0.94)
        pixels_per_mm = (detected_radius * 2) / plate_diameter_mm

        left_start = (
            int(center_x + config["left_start_offset_x"]),
            int(center_y + config["left_start_offset_y"])
        )

        right_start = (
            int(center_x + config["right_start_offset_x"]),
            int(center_y + config["right_start_offset_y"])
        )

        return {
            "pixels_per_mm": pixels_per_mm,
            "plate_center": (center_x, center_y),
            "plate_radius": analysis_radius,
            "split_x": center_x,
            "left_start": left_start,
            "right_start": right_start
        }

    plate_radius_pixels = config["plate_radius_pixels"]
    pixels_per_mm = (plate_radius_pixels * 2) / plate_diameter_mm

    return {
        "pixels_per_mm": pixels_per_mm,
        "plate_center": (config["plate_center_x"], config["plate_center_y"]),
        "plate_radius": config["plate_radius_pixels"],
        "split_x": config["split_x"],
        "left_start": (config["left_start_x"], config["left_start_y"]),
        "right_start": (config["right_start_x"], config["right_start_y"])
    }


def _copy_failed_image(image_path, failed_dir):
    """
    Copy a failed image into the failed-image QC folder.
    """

    if failed_dir is None:
        return

    failed_dir = Path(failed_dir)
    failed_dir.mkdir(parents=True, exist_ok=True)

    destination = failed_dir / Path(image_path).name
    shutil.copy2(image_path, destination)


def analyze_dual_culture_folder(
    input_folder,
    output_csv,
    annotated_folder,
    config_path,
    plot_path,
    report_path,
    failed_folder=None
):
    """
    Analyze a folder of dual-culture plate images.
    """

    image_dir = Path(input_folder)
    output_csv = Path(output_csv)
    annotated_dir = Path(annotated_folder)
    config_path = Path(config_path)
    plot_path = Path(plot_path)
    report_path = Path(report_path)

    if failed_folder is not None:
        failed_folder = Path(failed_folder)
        failed_folder.mkdir(parents=True, exist_ok=True)

    with open(config_path, "r") as file:
        config = json.load(file)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    annotated_dir.mkdir(parents=True, exist_ok=True)
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    image_paths = sorted(
        list(image_dir.glob("*.png")) +
        list(image_dir.glob("*.jpg")) +
        list(image_dir.glob("*.jpeg"))
    )

    results = []

    for image_path in image_paths:
        settings = get_analysis_settings(image_path, config)

        if settings is None:
            result = {
                "image": image_path.name,
                "detected": False,
                "failure_reason": "Petri dish not detected"
            }
            metadata = parse_plate_metadata(image_path.name)
            result.update(metadata)
            results.append(result)

            _copy_failed_image(image_path, failed_folder)
            continue

        result = analyze_dual_culture_image(
            image_path=image_path,
            pixels_per_mm=settings["pixels_per_mm"],
            threshold=config["threshold"],
            plate_center=settings["plate_center"],
            plate_radius=settings["plate_radius"],
            split_x=settings["split_x"],
            left_start=settings["left_start"],
            right_start=settings["right_start"],
            save_annotated=True,
            annotated_dir=annotated_dir
        )

        metadata = parse_plate_metadata(image_path.name)
        result.update(metadata)

        result["pixels_per_mm"] = settings["pixels_per_mm"]
        result["plate_center_x"] = settings["plate_center"][0]
        result["plate_center_y"] = settings["plate_center"][1]
        result["plate_radius_pixels"] = settings["plate_radius"]

        if result.get("detected") is False:
            _copy_failed_image(image_path, failed_folder)

        results.append(result)

    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)

    summary_by_day = None

    required_plot_columns = {"day", "left_width_mm", "right_width_mm", "gap_mm"}

    if required_plot_columns.issubset(df.columns):
        detected_df = df[df["detected"] == True].copy()

        if len(detected_df) > 0 and detected_df["day"].notna().any():
            summary_by_day = plot_dual_culture_summary(output_csv, plot_path)

    create_dual_culture_report(output_csv, report_path)

    return {
        "dataframe": df,
        "summary_by_day": summary_by_day,
        "output_csv": output_csv,
        "annotated_dir": annotated_dir,
        "failed_dir": failed_folder,
        "plot_path": plot_path,
        "report_path": report_path,
        "config_path": config_path
    }
