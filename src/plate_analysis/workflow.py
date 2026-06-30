
from pathlib import Path

from plate_analysis.pipeline import analyze_dual_culture_folder
from plate_analysis.quality_control import add_qc_flags
from plate_analysis.qc import create_contact_sheet
from plate_analysis.summary import create_experiment_summary
from plate_analysis.experiment_plots import plot_experiment_measurement


def run_dual_culture_workflow(
    input_folder,
    output_dir,
    config_path,
    prefix="analysis",
    gap_min_mm=0,
    gap_max_mm=None,
    plot_measurement="gap_mm",
    group_columns=None
):
    """
    Run the full BioVisionLab dual-culture workflow.

    Outputs:
    - results CSV
    - annotated QC images
    - analysis report
    - basic growth/gap plot
    - QC-flagged CSV
    - QC contact sheet
    - experiment summary CSV
    - experiment measurement plot
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results_csv = output_dir / f"{prefix}_results.csv"
    annotated_dir = output_dir / f"{prefix}_annotated"
    basic_plot = output_dir / f"{prefix}_basic_plot.png"
    report = output_dir / f"{prefix}_report.txt"
    failed_dir = output_dir / f"{prefix}_failed_images"

    qc_csv = output_dir / f"{prefix}_qc_flags.csv"
    contact_sheet = output_dir / f"{prefix}_contact_sheet.png"
    experiment_summary = output_dir / f"{prefix}_experiment_summary.csv"
    experiment_plot = output_dir / f"{prefix}_{plot_measurement}_plot.png"

    outputs = {
        "results_csv": results_csv,
        "annotated_dir": annotated_dir,
        "basic_plot": basic_plot,
        "report": report,
        "failed_dir": failed_dir,
        "qc_csv": qc_csv,
        "contact_sheet": contact_sheet,
        "experiment_summary": experiment_summary,
        "experiment_plot": experiment_plot
    }

    analysis_result = analyze_dual_culture_folder(
        input_folder=input_folder,
        output_csv=results_csv,
        annotated_folder=annotated_dir,
        config_path=config_path,
        plot_path=basic_plot,
        report_path=report,
        failed_folder=failed_dir
    )

    outputs["n_images"] = len(analysis_result["dataframe"])
    outputs["n_detected"] = int(analysis_result["dataframe"]["detected"].sum())

    add_qc_flags(
        results_csv=results_csv,
        output_csv=qc_csv,
        gap_min_mm=gap_min_mm,
        gap_max_mm=gap_max_mm
    )

    create_contact_sheet(
        image_folder=annotated_dir,
        output_path=contact_sheet,
        n_columns=4,
        thumbnail_width=300
    )

    try:
        create_experiment_summary(
            results_csv=results_csv,
            output_csv=experiment_summary,
            group_columns=group_columns
        )
        outputs["experiment_summary_created"] = True
    except Exception as error:
        outputs["experiment_summary_created"] = False
        outputs["experiment_summary_error"] = str(error)

    try:
        plot_experiment_measurement(
            results_csv=results_csv,
            output_plot=experiment_plot,
            measurement=plot_measurement,
            group_columns=group_columns
        )
        outputs["experiment_plot_created"] = True
    except Exception as error:
        outputs["experiment_plot_created"] = False
        outputs["experiment_plot_error"] = str(error)

    return outputs
