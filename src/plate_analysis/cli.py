
from pathlib import Path
import argparse

from plate_analysis.pipeline import analyze_dual_culture_folder
from plate_analysis.qc import create_contact_sheet
from plate_analysis.validation import validate_gap_measurements
from plate_analysis.preview import create_config_preview
from plate_analysis.summary import create_experiment_summary
from plate_analysis.quality_control import add_qc_flags
from plate_analysis.manual_validation import compare_with_manual_measurements, create_manual_measurement_template
from plate_analysis.experiment_plots import plot_experiment_measurement
from plate_analysis.workflow import run_dual_culture_workflow


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
    parser.add_argument("--failed", default=None, help="Folder to save failed input images")

    args = parser.parse_args()

    result = analyze_dual_culture_folder(
        input_folder=args.input,
        output_csv=args.output,
        annotated_folder=args.annotated,
        config_path=args.config,
        plot_path=args.plot,
        report_path=args.report,
        failed_folder=args.failed
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
    if result.get("failed_dir") is not None:
        print(f"Failed images saved at: {result['failed_dir']}")

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


def main_compare_manual():
    parser = argparse.ArgumentParser(
        description="Compare BioVisionLab automated measurements with manual measurements."
    )

    parser.add_argument("--input", required=True, help="BioVisionLab results CSV")
    parser.add_argument("--manual", required=True, help="Manual measurement CSV")
    parser.add_argument("--output", required=True, help="Output CSV with errors")
    parser.add_argument("--plot", required=True, help="Output validation plot")
    parser.add_argument("--report", required=True, help="Output validation report")

    args = parser.parse_args()

    metrics = compare_with_manual_measurements(
        results_csv=args.input,
        manual_csv=args.manual,
        output_csv=args.output,
        output_plot=args.plot,
        output_report=args.report
    )

    print("BioVisionLab manual validation complete")
    print("--------------------------------------")
    print(f"Automated results: {args.input}")
    print(f"Manual measurements: {args.manual}")
    print(f"Output CSV: {args.output}")
    print(f"Plot: {args.plot}")
    print(f"Report: {args.report}")
    print("")
    print(metrics)


def main_manual_template():
    parser = argparse.ArgumentParser(
        description="Create a blank manual-measurement template from BioVisionLab results."
    )

    parser.add_argument("--input", required=True, help="BioVisionLab results CSV")
    parser.add_argument("--output", required=True, help="Output manual-measurement template CSV")
    parser.add_argument(
        "--include-failed",
        action="store_true",
        help="Include failed detections in the manual template"
    )

    args = parser.parse_args()

    template = create_manual_measurement_template(
        results_csv=args.input,
        output_csv=args.output,
        include_detected_only=not args.include_failed
    )

    print("Manual measurement template created")
    print("-----------------------------------")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Rows: {len(template)}")


def main_plot_experiment():
    parser = argparse.ArgumentParser(
        description="Plot BioVisionLab measurements over time."
    )

    parser.add_argument("--input", required=True, help="BioVisionLab results CSV")
    parser.add_argument("--output", required=True, help="Output plot image")
    parser.add_argument(
        "--measurement",
        default="gap_mm",
        help="Measurement column to plot, for example gap_mm or left_width_mm"
    )
    parser.add_argument(
        "--group-by",
        nargs="+",
        default=None,
        help="Optional grouping columns, for example cultivar treatment"
    )

    args = parser.parse_args()

    summary = plot_experiment_measurement(
        results_csv=args.input,
        output_plot=args.output,
        measurement=args.measurement,
        group_columns=args.group_by
    )

    print("BioVisionLab experiment plot created")
    print("------------------------------------")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Measurement: {args.measurement}")
    print(f"Rows in plot summary: {len(summary)}")
    print("")
    print(summary.head())


def main_run_workflow():
    parser = argparse.ArgumentParser(
        description="Run the full BioVisionLab dual-culture workflow."
    )

    parser.add_argument("--input", required=True, help="Folder containing plate images")
    parser.add_argument("--output-dir", required=True, help="Folder to save all workflow outputs")
    parser.add_argument("--config", required=True, help="BioVisionLab config JSON file")
    parser.add_argument("--prefix", default="analysis", help="Prefix for output files")
    parser.add_argument("--gap-min-mm", type=float, default=0, help="Minimum acceptable gap in mm")
    parser.add_argument("--gap-max-mm", type=float, default=None, help="Maximum acceptable gap in mm")
    parser.add_argument("--plot-measurement", default="gap_mm", help="Measurement to plot")
    parser.add_argument(
        "--group-by",
        nargs="+",
        default=None,
        help="Optional grouping columns, for example cultivar treatment day"
    )

    args = parser.parse_args()

    outputs = run_dual_culture_workflow(
        input_folder=args.input,
        output_dir=args.output_dir,
        config_path=args.config,
        prefix=args.prefix,
        gap_min_mm=args.gap_min_mm,
        gap_max_mm=args.gap_max_mm,
        plot_measurement=args.plot_measurement,
        group_columns=args.group_by
    )

    print("BioVisionLab full workflow complete")
    print("-----------------------------------")
    print(f"Images analyzed: {outputs['n_images']}")
    print(f"Detected successfully: {outputs['n_detected']}")
    print("")
    print("Outputs:")
    print(f"Results CSV: {outputs['results_csv']}")
    print(f"Annotated images: {outputs['annotated_dir']}")
    print(f"Report: {outputs['report']}")
    print(f"QC CSV: {outputs['qc_csv']}")
    print(f"Contact sheet: {outputs['contact_sheet']}")

    if outputs.get("experiment_summary_created"):
        print(f"Experiment summary: {outputs['experiment_summary']}")
    else:
        print(f"Experiment summary skipped: {outputs.get('experiment_summary_error')}")

    if outputs.get("experiment_plot_created"):
        print(f"Experiment plot: {outputs['experiment_plot']}")
    else:
        print(f"Experiment plot skipped: {outputs.get('experiment_plot_error')}")
