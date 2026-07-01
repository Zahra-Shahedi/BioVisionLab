
from pathlib import Path
import json


def validate_config(config_path, output_report=None):
    config_path = Path(config_path)

    with open(config_path, "r") as file:
        config = json.load(file)

    errors = []
    warnings = []

    required_common = [
        "plate_diameter_mm",
        "threshold",
        "plate_radius_pixels"
    ]

    for key in required_common:
        if key not in config:
            errors.append(f"Missing required key: {key}")

    threshold_method = config.get("threshold_method", "global")

    allowed_methods = ["global", "otsu", "adaptive"]

    if threshold_method not in allowed_methods:
        errors.append(
            f"Invalid threshold_method: {threshold_method}. "
            f"Allowed values: {allowed_methods}"
        )

    if "plate_diameter_mm" in config and config["plate_diameter_mm"] <= 0:
        errors.append("plate_diameter_mm must be greater than 0.")

    if "threshold" in config:
        threshold = config["threshold"]

        if threshold < 0 or threshold > 255:
            errors.append("threshold must be between 0 and 255.")

    plate_radius_pixels = config.get("plate_radius_pixels", None)

    if plate_radius_pixels == "auto":
        required_auto = [
            "left_start_offset_x",
            "left_start_offset_y",
            "right_start_offset_x",
            "right_start_offset_y"
        ]

        for key in required_auto:
            if key not in config:
                errors.append(f"Missing required auto-detection key: {key}")

    else:
        required_fixed = [
            "plate_center_x",
            "plate_center_y",
            "split_x",
            "left_start_x",
            "left_start_y",
            "right_start_x",
            "right_start_y"
        ]

        for key in required_fixed:
            if key not in config:
                errors.append(f"Missing required fixed-config key: {key}")

        if plate_radius_pixels is not None:
            if not isinstance(plate_radius_pixels, (int, float)):
                errors.append("plate_radius_pixels must be a number or 'auto'.")
            elif plate_radius_pixels <= 0:
                errors.append("plate_radius_pixels must be greater than 0.")

    adaptive_block_size = config.get("adaptive_block_size", 51)

    if adaptive_block_size % 2 == 0:
        warnings.append("adaptive_block_size is even. BioVisionLab will adjust it to the next odd number.")

    if adaptive_block_size < 3:
        errors.append("adaptive_block_size must be at least 3.")

    for key in ["open_kernel_size", "close_kernel_size"]:
        value = config.get(key, 0)

        if value < 0:
            errors.append(f"{key} must be 0 or greater.")

    min_colony_area_px = config.get("min_colony_area_px", 50)

    if min_colony_area_px <= 0:
        errors.append("min_colony_area_px must be greater than 0.")

    is_valid = len(errors) == 0

    result = {
        "config_path": config_path,
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings
    }

    if output_report is not None:
        output_report = Path(output_report)
        output_report.parent.mkdir(parents=True, exist_ok=True)

        lines = []
        lines.append("BioVisionLab Config Validation Report")
        lines.append("====================================")
        lines.append("")
        lines.append(f"Config file: {config_path}")
        lines.append(f"Valid: {is_valid}")
        lines.append("")

        if errors:
            lines.append("Errors")
            lines.append("------")
            for error in errors:
                lines.append(f"- {error}")
            lines.append("")
        else:
            lines.append("Errors: none")
            lines.append("")

        if warnings:
            lines.append("Warnings")
            lines.append("--------")
            for warning in warnings:
                lines.append(f"- {warning}")
            lines.append("")
        else:
            lines.append("Warnings: none")
            lines.append("")

        output_report.write_text("\n".join(lines))
        result["output_report"] = output_report

    return result
