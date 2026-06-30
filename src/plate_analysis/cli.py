
from pathlib import Path
import argparse

from plate_analysis.pipeline import analyze_dual_culture_folder
from plate_analysis.qc import create_contact_sheet
from plate_analysis.validation import validate_gap_measurements
from plate_analysis.preview import create_config_preview
from plate_analysis.summary import create_experiment_summary
from plate_analysis.quality_control import add_qc_flags


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


def main_summarize():
    parser = argparse.ArgumentParser(
        description="Create grouped summary tables from BioVisionLab results."
    )

    parser.add_argument("--input", required=True, help="BioVisionLab results CSV")
    parser.add_argument("--output", required=True, help="Output summary CSV")
    parser.add_argument(
        "--group-by",
        nargs="+",
        default=None,
        help="Columns to group by, for example: cultivar treatment day"
    )

    args = parser.parse_args()

    summary = create_experiment_summary(
        results_csv=args.input,
        output_csv=args.output,
        group_columns=args.group_by
    )

    print("BioVisionLab experiment summary created")
    print("--------------------------------------")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Rows: {len(summary)}")
    print("")
    print(summary.head())


def main_qc_flags():
    parser = argparse.ArgumentParser(
        description="Add quality-control flags to BioVisionLab results."
    )

    parser.add_argument("--input", required=True, help="BioVisionLab results CSV")
    parser.add_argument("--output", required=True, help="Output CSV with QC flags")
    parser.add_argument("--gap-min-mm", type=float, default=0, help="Minimum acceptable gap in mm")
    parser.add_argument("--gap-max-mm", type=float, default=None, help="Maximum acceptable gap in mm")

    args = parser.parse_args()

    df = add_qc_flags(
        results_csv=args.input,
        output_csv=args.output,
        gap_min_mm=args.gap_min_mm,
        gap_max_mm=args.gap_max_mm
    )

    n_check = (df["qc_flag"] == "check").sum()
    n_pass = (df["qc_flag"] == "pass").sum()

    print("BioVisionLab QC flags added")
    print("---------------------------")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Passed rows: {n_pass}")
    print(f"Rows needing check: {n_check}")

    if n_check > 0:
        print("")
        print("Rows needing check:")
        print(df[df["qc_flag"] == "check"][["image", "qc_reason"]].head(20))
