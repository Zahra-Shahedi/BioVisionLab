
from pathlib import Path
import argparse

from plate_analysis.pipeline import analyze_dual_culture_folder
from plate_analysis.qc import create_contact_sheet
from plate_analysis.validation import validate_gap_measurements
from plate_analysis.preview import create_config_preview


def main_analyze():
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

    result = analyze_dual_culture_folder(
        input_folder=args.input,
        output_csv=args.output,
        annotated_folder=args.annotated,
        config_path=args.config,
        plot_path=args.plot,
        report_path=args.report
    )

    df = result["dataframe"]

    print("BioVisionLab dual-culture analysis complete")
    print("------------------------------------------")
    print(f"Images analyzed: {len(df)}")
    print(f"Detected successfully: {df['detected'].sum()}")
    print(f"Config used: {result['config_path']}")
    print(f"CSV saved at: {result['output_csv']}")
    print(f"Annotated images saved at: {result['annotated_dir']}")
    print(f"Summary plot saved at: {result['plot_path']}")
    print(f"Report saved at: {result['report_path']}")

    if result["summary_by_day"] is not None:
        print("\nSummary by day:")
        print(result["summary_by_day"])


def main_contact_sheet():
    parser = argparse.ArgumentParser(
        description="Create a QC contact sheet from annotated BioVisionLab images."
    )

    parser.add_argument("--input", required=True, help="Folder containing annotated images")
    parser.add_argument("--output", required=True, help="Path to save contact sheet image")
    parser.add_argument("--columns", type=int, default=4, help="Number of columns")
    parser.add_argument("--thumbnail-width", type=int, default=300, help="Thumbnail width in pixels")

    args = parser.parse_args()

    output_path = create_contact_sheet(
        image_folder=args.input,
        output_path=args.output,
        n_columns=args.columns,
        thumbnail_width=args.thumbnail_width
    )

    print("QC contact sheet created")
    print("------------------------")
    print(f"Saved at: {output_path}")


def main_validate_mock():
    project_dir = Path.cwd()

    metrics = validate_gap_measurements(
        results_csv=project_dir / "results" / "demo_results.csv",
        ground_truth_csv=project_dir / "results" / "mock_dataset_ground_truth.csv",
        output_csv=project_dir / "results" / "demo_validation.csv",
        output_plot=project_dir / "results" / "demo_validation_plot.png",
        output_report=project_dir / "results" / "demo_validation_report.txt"
    )

    print("BioVisionLab validation complete")
    print("--------------------------------")
    print(f"Images compared: {metrics['images_compared']}")
    print(f"Mean error: {metrics['mean_error_mm']:.3f} mm")
    print(f"Mean absolute error: {metrics['mean_absolute_error_mm']:.3f} mm")
    print(f"RMSE: {metrics['rmse_mm']:.3f} mm")
    print(f"Maximum absolute error: {metrics['max_absolute_error_mm']:.3f} mm")


def main_preview_config():
    parser = argparse.ArgumentParser(
        description="Preview BioVisionLab plate detection and plug-position settings."
    )

    parser.add_argument("--image", required=True, help="Input plate image")
    parser.add_argument("--config", required=True, help="BioVisionLab config JSON file")
    parser.add_argument("--output", required=True, help="Output preview image")

    args = parser.parse_args()

    result = create_config_preview(
        image_path=args.image,
        config_path=args.config,
        output_path=args.output
    )

    print("BioVisionLab config preview created")
    print("-----------------------------------")
    print(f"Saved at: {result['output_path']}")
    print(f"Plate center: {result['plate_center']}")
    print(f"Plate radius: {result['plate_radius']}")
    print(f"Split x: {result['split_x']}")
    print(f"Left plug estimate: {result['left_start']}")
    print(f"Right plug estimate: {result['right_start']}")
