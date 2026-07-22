
from pathlib import Path
import argparse

from plate_analysis.pipeline import analyze_dual_culture_folder
from plate_analysis.qc import create_contact_sheet
from plate_analysis.validation import validate_gap_measurements
from plate_analysis.preview import create_config_preview
from plate_analysis.summary import create_experiment_summary
from plate_analysis.quality_control import add_qc_flags, copy_qc_review_images
from plate_analysis.manual_validation import compare_with_manual_measurements, create_manual_measurement_template
from plate_analysis.experiment_plots import plot_experiment_measurement
from plate_analysis.workflow import run_dual_culture_workflow
from plate_analysis.dataset_audit import audit_image_folder
from plate_analysis.experiment_setup import initialize_experiment_folder
from plate_analysis.synthetic_data import generate_mock_dual_culture_dataset
from plate_analysis.threshold_compare import compare_threshold_methods
from plate_analysis.mask_preview import create_mask_preview
from plate_analysis.config_validation import validate_config
from plate_analysis.seeded_pipeline import analyze_seeded_folder
from plate_analysis.seeded_plots import plot_seeded_results


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


def main_qc_review_images():
    parser = argparse.ArgumentParser(
        description="Copy QC-flagged annotated images into a review folder."
    )

    parser.add_argument("--qc-csv", required=True, help="CSV containing qc_flag column")
    parser.add_argument("--annotated", required=True, help="Folder containing annotated images")
    parser.add_argument("--output", required=True, help="Folder to copy flagged images into")

    args = parser.parse_args()

    summary = copy_qc_review_images(
        qc_csv=args.qc_csv,
        annotated_folder=args.annotated,
        output_folder=args.output
    )

    print("BioVisionLab QC review images copied")
    print("------------------------------------")
    print(f"Flagged rows: {summary['n_flagged']}")
    print(f"Images copied: {summary['n_copied']}")
    print(f"Missing annotated images: {summary['n_missing']}")
    print(f"Output folder: {args.output}")

    if summary["n_missing"] > 0:
        print("")
        print("Missing:")
        for name in summary["missing"][:20]:
            print(f"- {name}")


def main_audit_dataset():
    parser = argparse.ArgumentParser(
        description="Audit image folder before BioVisionLab analysis."
    )

    parser.add_argument("--input", required=True, help="Folder containing images")
    parser.add_argument("--output", required=True, help="Output audit CSV")
    parser.add_argument("--config", default=None, help="Optional BioVisionLab config JSON file")
    parser.add_argument("--report", default=None, help="Optional text audit report")

    args = parser.parse_args()

    audit = audit_image_folder(
        input_folder=args.input,
        output_csv=args.output,
        config_path=args.config,
        output_report=args.report
    )

    print("BioVisionLab dataset audit complete")
    print("-----------------------------------")
    print(f"Images found: {len(audit)}")
    print(f"Readable images: {int(audit['readable'].sum())}")
    print(f"Audit CSV: {args.output}")

    if args.report is not None:
        print(f"Audit report: {args.report}")

    if "config_ok" in audit.columns and audit["config_ok"].notna().any():
        print(f"Images passing config check: {int((audit['config_ok'] == True).sum())}")
        print(f"Images failing config check: {int((audit['config_ok'] == False).sum())}")


def main_init_experiment():
    parser = argparse.ArgumentParser(
        description="Create a starter folder structure for a new BioVisionLab experiment."
    )

    parser.add_argument("--output-dir", required=True, help="Experiment folder to create")
    parser.add_argument("--plate-diameter-mm", type=float, default=90, help="Petri dish diameter in mm")
    parser.add_argument("--threshold", type=int, default=220, help="Fungal colony threshold")
    parser.add_argument("--left-start-offset-x", type=int, default=-90, help="Left plug x offset from plate center")
    parser.add_argument("--right-start-offset-x", type=int, default=90, help="Right plug x offset from plate center")

    args = parser.parse_args()

    result = initialize_experiment_folder(
        output_dir=args.output_dir,
        plate_diameter_mm=args.plate_diameter_mm,
        threshold=args.threshold,
        left_start_offset_x=args.left_start_offset_x,
        right_start_offset_x=args.right_start_offset_x
    )

    print("BioVisionLab experiment folder created")
    print("--------------------------------------")
    print(f"Experiment folder: {result['output_dir']}")
    print(f"Raw image folder: {result['data_dir']}")
    print(f"Results folder: {result['results_dir']}")
    print(f"Config file: {result['config_path']}")
    print(f"Experiment README: {result['readme_path']}")


def main_generate_demo():
    parser = argparse.ArgumentParser(
        description="Generate a mock dual-culture image dataset for BioVisionLab demos."
    )

    parser.add_argument("--image-dir", required=True, help="Folder to save generated mock images")
    parser.add_argument("--ground-truth", required=True, help="Path to save ground-truth CSV")
    parser.add_argument("--n-plates", type=int, default=10, help="Number of mock plates")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()

    result = generate_mock_dual_culture_dataset(
        image_dir=args.image_dir,
        ground_truth_csv=args.ground_truth,
        n_plates=args.n_plates,
        seed=args.seed
    )

    print("BioVisionLab mock dataset generated")
    print("-----------------------------------")
    print(f"Images saved at: {result['image_dir']}")
    print(f"Ground truth saved at: {result['ground_truth_csv']}")
    print(f"Images created: {result['n_images']}")


def main_compare_thresholds():
    parser = argparse.ArgumentParser(
        description="Compare BioVisionLab threshold methods on one image."
    )

    parser.add_argument("--image", required=True, help="Input plate image")
    parser.add_argument("--config", required=True, help="BioVisionLab config JSON file")
    parser.add_argument("--output-dir", required=True, help="Folder to save comparison outputs")
    parser.add_argument(
        "--methods",
        nargs="+",
        default=["global", "otsu", "adaptive"],
        help="Threshold methods to compare"
    )

    args = parser.parse_args()

    result = compare_threshold_methods(
        image_path=args.image,
        config_path=args.config,
        output_dir=args.output_dir,
        methods=args.methods
    )

    print("BioVisionLab threshold comparison complete")
    print("-----------------------------------------")
    print(f"Image: {args.image}")
    print(f"Config: {args.config}")
    print(f"Output folder: {result['output_dir']}")
    print(f"Comparison CSV: {result['comparison_csv']}")
    print("")
    print(result["dataframe"][["method_tested", "detected", "gap_mm", "failure_reason"]])


def main_preview_mask():
    parser = argparse.ArgumentParser(
        description="Create a BioVisionLab fungus-mask preview for one image."
    )

    parser.add_argument("--image", required=True, help="Input plate image")
    parser.add_argument("--config", required=True, help="BioVisionLab config JSON file")
    parser.add_argument("--output-dir", required=True, help="Folder to save mask preview outputs")

    args = parser.parse_args()

    result = create_mask_preview(
        image_path=args.image,
        config_path=args.config,
        output_dir=args.output_dir
    )

    print("BioVisionLab mask preview created")
    print("---------------------------------")
    print(f"Threshold method: {result['threshold_method']}")
    print(f"Mask area: {result['mask_area_px']} pixels")
    print(f"Gray image: {result['gray_path']}")
    print(f"Fungus mask: {result['mask_path']}")
    print(f"Overlay: {result['overlay_path']}")


def main_validate_config():
    parser = argparse.ArgumentParser(
        description="Validate a BioVisionLab config JSON file."
    )

    parser.add_argument("--config", required=True, help="BioVisionLab config JSON file")
    parser.add_argument("--report", default=None, help="Optional output validation report")

    args = parser.parse_args()

    result = validate_config(
        config_path=args.config,
        output_report=args.report
    )

    print("BioVisionLab config validation complete")
    print("--------------------------------------")
    print(f"Config: {result['config_path']}")
    print(f"Valid: {result['is_valid']}")

    if result["errors"]:
        print("")
        print("Errors:")
        for error in result["errors"]:
            print(f"- {error}")

    if result["warnings"]:
        print("")
        print("Warnings:")
        for warning in result["warnings"]:
            print(f"- {warning}")

    if args.report is not None:
        print("")
        print(f"Report saved at: {args.report}")


def main_analyze_seeded():
    parser = argparse.ArgumentParser(
        description="Analyze dual-culture plates using seeded colony segmentation."
    )

    parser.add_argument("--input", required=True, help="Input image folder")
    parser.add_argument("--config", required=True, help="Seeded segmentation config JSON")
    parser.add_argument("--output-csv", required=True, help="Output measurements CSV")
    parser.add_argument("--annotated-dir", required=True, help="Output annotated image folder")
    parser.add_argument("--calibration-csv", default=None, help="Optional per-image calibration CSV")

    args = parser.parse_args()

    df = analyze_seeded_folder(
        input_dir=args.input,
        config_path=args.config,
        output_csv=args.output_csv,
        annotated_dir=args.annotated_dir,
        calibration_csv=args.calibration_csv
    )

    print("BioVisionLab seeded analysis complete")
    print("------------------------------------")
    print(f"Images analyzed: {len(df)}")
    print(f"Detected: {df['detected'].sum()}")
    print(f"Failed: {(~df['detected']).sum()}")
    print(f"Output CSV: {args.output_csv}")
    print(f"Annotated images: {args.annotated_dir}")


def main_plot_seeded():
    parser = argparse.ArgumentParser(
        description="Create plots from BioVisionLab seeded segmentation measurements."
    )

    parser.add_argument("--csv", required=True, help="Seeded measurements CSV")
    parser.add_argument("--output-dir", required=True, help="Folder to save plots")
    parser.add_argument("--day-column", default="day", help="Column to use as time/day")

    args = parser.parse_args()

    outputs = plot_seeded_results(
        csv_path=args.csv,
        output_dir=args.output_dir,
        day_column=args.day_column
    )

    print("BioVisionLab seeded plots created")
    print("--------------------------------")
    for name, path in outputs.items():
        print(f"{name}: {path}")
