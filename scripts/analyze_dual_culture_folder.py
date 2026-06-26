
from pathlib import Path
import sys
import argparse
import json
import pandas as pd

project_dir = Path.home() / "BioVisionLab"
sys.path.append(str(project_dir / "src"))

from plate_analysis.dual_culture import analyze_dual_culture_image
from plate_analysis.metadata import parse_plate_metadata
from plate_analysis.plotting import plot_dual_culture_summary
from plate_analysis.reporting import create_dual_culture_report


def main():
    parser = argparse.ArgumentParser(
        description="Analyze dual-culture Petri dish images using BioVisionLab."
    )

    parser.add_argument("--input", required=True, help="Folder containing plate images")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    parser.add_argument("--annotated", required=True, help="Folder to save annotated images")
    parser.add_argument("--config", required=True, help="Path to JSON config file")
    parser.add_argument("--plot", required=True, help="Path to save summary plot")
    parser.add_argument("--report", required=True, help="Path to save text report")

    args = parser.parse_args()

    image_dir = Path(args.input)
    output_csv = Path(args.output)
    annotated_dir = Path(args.annotated)
    config_path = Path(args.config)
    plot_path = Path(args.plot)
    report_path = Path(args.report)

    with open(config_path, "r") as file:
        config = json.load(file)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    annotated_dir.mkdir(parents=True, exist_ok=True)
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    plate_diameter_mm = config["plate_diameter_mm"]
    plate_radius_pixels = config["plate_radius_pixels"]
    plate_diameter_pixels = plate_radius_pixels * 2
    pixels_per_mm = plate_diameter_pixels / plate_diameter_mm

    image_paths = sorted(
        list(image_dir.glob("*.png")) +
        list(image_dir.glob("*.jpg")) +
        list(image_dir.glob("*.jpeg"))
    )

    results = []

    for image_path in image_paths:
        result = analyze_dual_culture_image(
            image_path=image_path,
            pixels_per_mm=pixels_per_mm,
            threshold=config["threshold"],
            plate_center=(config["plate_center_x"], config["plate_center_y"]),
            plate_radius=config["plate_radius_pixels"],
            split_x=config["split_x"],
            left_start=(config["left_start_x"], config["left_start_y"]),
            right_start=(config["right_start_x"], config["right_start_y"]),
            save_annotated=True,
            annotated_dir=annotated_dir
        )

        metadata = parse_plate_metadata(image_path.name)
        result.update(metadata)

        results.append(result)

    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)

    summary_by_day = plot_dual_culture_summary(output_csv, plot_path)
    create_dual_culture_report(output_csv, report_path)

    print("BioVisionLab dual-culture analysis complete")
    print("------------------------------------------")
    print(f"Images analyzed: {len(df)}")
    print(f"Detected successfully: {df['detected'].sum()}")
    print(f"Config used: {config_path}")
    print(f"CSV saved at: {output_csv}")
    print(f"Annotated images saved at: {annotated_dir}")
    print(f"Summary plot saved at: {plot_path}")
    print(f"Report saved at: {report_path}")

    print("\nSummary by day:")
    print(summary_by_day)


if __name__ == "__main__":
    main()
