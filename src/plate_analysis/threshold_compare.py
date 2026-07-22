
from pathlib import Path
import json
import pandas as pd

from plate_analysis.pipeline import get_analysis_settings
from plate_analysis.dual_culture import analyze_dual_culture_image


def compare_threshold_methods(
    image_path,
    config_path,
    output_dir,
    methods=None
):
    """
    Compare threshold methods on one image.

    Saves:
    - annotated images for each method
    - CSV summary of measurements
    """

    image_path = Path(image_path)
    config_path = Path(config_path)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    if methods is None:
        methods = ["global", "otsu", "adaptive"]

    with open(config_path, "r") as file:
        config = json.load(file)

    settings = get_analysis_settings(image_path, config)

    if settings is None:
        raise ValueError("Could not detect/apply plate settings for this image.")

    rows = []

    for method in methods:
        method = str(method).lower()

        annotated_dir = output_dir / f"{method}_annotated"

        result = analyze_dual_culture_image(
            image_path=image_path,
            pixels_per_mm=settings["pixels_per_mm"],
            threshold=config.get("threshold", 220),
            plate_center=settings["plate_center"],
            plate_radius=settings["plate_radius"],
            split_x=settings["split_x"],
            left_start=settings["left_start"],
            right_start=settings["right_start"],
            save_annotated=True,
            annotated_dir=annotated_dir,
            threshold_method=method,
            adaptive_block_size=config.get("adaptive_block_size", 51),
            adaptive_c=config.get("adaptive_c", 2),
            open_kernel_size=config.get("open_kernel_size", 0),
            close_kernel_size=config.get("close_kernel_size", 0),
            min_colony_area_px=config.get("min_colony_area_px", 50)
        )

        result["method_tested"] = method
        result["annotated_folder"] = str(annotated_dir)

        rows.append(result)

    comparison = pd.DataFrame(rows)

    output_csv = output_dir / "threshold_comparison.csv"
    comparison.to_csv(output_csv, index=False)

    return {
        "comparison_csv": output_csv,
        "dataframe": comparison,
        "output_dir": output_dir
    }
