
from pathlib import Path
import cv2
import pandas as pd

from plate_analysis.pipeline import get_analysis_settings


def audit_image_folder(
    input_folder,
    output_csv,
    config_path=None,
    output_report=None
):
    """
    Audit a folder of images before full BioVisionLab analysis.

    The audit checks:
    - image readability
    - image width and height
    - file extension
    - whether BioVisionLab config/plate settings can be applied
    """

    input_folder = Path(input_folder)
    output_csv = Path(output_csv)

    if output_report is not None:
        output_report = Path(output_report)

    image_paths = sorted(
        list(input_folder.glob("*.png")) +
        list(input_folder.glob("*.jpg")) +
        list(input_folder.glob("*.jpeg"))
    )

    rows = []

    for image_path in image_paths:
        row = {
            "image": image_path.name,
            "extension": image_path.suffix.lower(),
            "readable": False,
            "width_px": None,
            "height_px": None,
            "config_ok": None,
            "plate_center_x": None,
            "plate_center_y": None,
            "plate_radius_pixels": None,
            "issue": ""
        }

        img = cv2.imread(str(image_path))

        if img is None:
            row["issue"] = "image_not_readable"
            rows.append(row)
            continue

        height, width = img.shape[:2]

        row["readable"] = True
        row["width_px"] = width
        row["height_px"] = height

        if config_path is not None:
            try:
                import json

                with open(config_path, "r") as file:
                    config = json.load(file)

                settings = get_analysis_settings(image_path, config)

                if settings is None:
                    row["config_ok"] = False
                    row["issue"] = "config_or_plate_detection_failed"
                else:
                    row["config_ok"] = True
                    row["plate_center_x"] = settings["plate_center"][0]
                    row["plate_center_y"] = settings["plate_center"][1]
                    row["plate_radius_pixels"] = settings["plate_radius"]

            except Exception as error:
                row["config_ok"] = False
                row["issue"] = f"config_error: {error}"

        rows.append(row)

    audit = pd.DataFrame(rows)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(output_csv, index=False)

    if output_report is not None:
        lines = []
        lines.append("BioVisionLab Dataset Audit Report")
        lines.append("=================================")
        lines.append("")
        lines.append(f"Input folder: {input_folder}")
        lines.append(f"Images found: {len(audit)}")

        if len(audit) > 0:
            lines.append(f"Readable images: {int(audit['readable'].sum())}")
            lines.append(f"Unreadable images: {int((audit['readable'] == False).sum())}")

            if "config_ok" in audit.columns and audit["config_ok"].notna().any():
                lines.append(f"Images passing config check: {int((audit['config_ok'] == True).sum())}")
                lines.append(f"Images failing config check: {int((audit['config_ok'] == False).sum())}")

            lines.append("")
            lines.append("Image dimensions")
            lines.append("----------------")
            readable = audit[audit["readable"] == True]

            if len(readable) > 0:
                size_counts = readable.groupby(["width_px", "height_px"]).size().reset_index(name="n")
                for _, row in size_counts.iterrows():
                    lines.append(f"{int(row['width_px'])} x {int(row['height_px'])}: {int(row['n'])} image(s)")

            issues = audit[audit["issue"].astype(str) != ""]

            if len(issues) > 0:
                lines.append("")
                lines.append("Issues")
                lines.append("------")
                for _, row in issues.iterrows():
                    lines.append(f"- {row['image']}: {row['issue']}")

        output_report.parent.mkdir(parents=True, exist_ok=True)

        with open(output_report, "w") as file:
            file.write("\n".join(lines))

    return audit
