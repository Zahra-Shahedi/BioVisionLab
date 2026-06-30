
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def compare_with_manual_measurements(
    results_csv,
    manual_csv,
    output_csv,
    output_plot,
    output_report,
    measurements=None
):
    """
    Compare BioVisionLab automated measurements with manual measurements.

    Manual CSV should contain:
    - image
    - manual_gap_mm
    - manual_left_width_mm
    - manual_right_width_mm

    Not all manual columns are required. The function uses whatever matching
    manual columns are available.
    """

    results_csv = Path(results_csv)
    manual_csv = Path(manual_csv)
    output_csv = Path(output_csv)
    output_plot = Path(output_plot)
    output_report = Path(output_report)

    results = pd.read_csv(results_csv)
    manual = pd.read_csv(manual_csv)

    if "image" not in results.columns or "image" not in manual.columns:
        raise ValueError("Both CSV files must contain an 'image' column.")

    if "detected" in results.columns:
        results = results[results["detected"] == True].copy()

    merged = results.merge(manual, on="image", how="inner")

    if len(merged) == 0:
        raise ValueError("No matching image names found between automated and manual CSV files.")

    default_measurements = {
        "gap_mm": "manual_gap_mm",
        "left_width_mm": "manual_left_width_mm",
        "right_width_mm": "manual_right_width_mm",
        "left_growth_toward_mm": "manual_left_growth_toward_mm",
        "right_growth_toward_mm": "manual_right_growth_toward_mm"
    }

    if measurements is None:
        measurements = default_measurements

    available_pairs = {}

    for auto_col, manual_col in measurements.items():
        if auto_col in merged.columns and manual_col in merged.columns:
            available_pairs[auto_col] = manual_col

    if len(available_pairs) == 0:
        raise ValueError("No matching automated/manual measurement columns found.")

    metrics = []

    for auto_col, manual_col in available_pairs.items():
        error_col = f"{auto_col}_error"
        abs_error_col = f"{auto_col}_absolute_error"

        merged[error_col] = merged[auto_col] - merged[manual_col]
        merged[abs_error_col] = merged[error_col].abs()

        mean_error = merged[error_col].mean()
        mean_absolute_error = merged[abs_error_col].mean()
        rmse = np.sqrt((merged[error_col] ** 2).mean())
        max_absolute_error = merged[abs_error_col].max()

        metrics.append({
            "measurement": auto_col,
            "manual_column": manual_col,
            "n_images": len(merged),
            "mean_error_mm": mean_error,
            "mean_absolute_error_mm": mean_absolute_error,
            "rmse_mm": rmse,
            "max_absolute_error_mm": max_absolute_error
        })

    metrics_df = pd.DataFrame(metrics)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_plot.parent.mkdir(parents=True, exist_ok=True)
    output_report.parent.mkdir(parents=True, exist_ok=True)

    merged.to_csv(output_csv, index=False)

    # Make validation plot for gap if available; otherwise use first available measurement.
    if "gap_mm" in available_pairs:
        plot_auto_col = "gap_mm"
    else:
        plot_auto_col = list(available_pairs.keys())[0]

    plot_manual_col = available_pairs[plot_auto_col]

    plt.figure(figsize=(6, 6))
    plt.scatter(merged[plot_manual_col], merged[plot_auto_col])

    min_value = min(merged[plot_manual_col].min(), merged[plot_auto_col].min())
    max_value = max(merged[plot_manual_col].max(), merged[plot_auto_col].max())

    plt.plot([min_value, max_value], [min_value, max_value], linestyle="--")
    plt.xlabel(f"Manual {plot_auto_col}")
    plt.ylabel(f"BioVisionLab {plot_auto_col}")
    plt.title("Manual vs automated measurement")
    plt.tight_layout()
    plt.savefig(output_plot, dpi=300)
    plt.close()

    lines = []
    lines.append("BioVisionLab Manual Validation Report")
    lines.append("====================================")
    lines.append("")
    lines.append(f"Automated results file: {results_csv.name}")
    lines.append(f"Manual measurements file: {manual_csv.name}")
    lines.append(f"Images compared: {len(merged)}")
    lines.append("")

    lines.append("Error metrics")
    lines.append("-------------")

    for _, row in metrics_df.iterrows():
        lines.append("")
        lines.append(f"Measurement: {row['measurement']}")
        lines.append(f"Manual column: {row['manual_column']}")
        lines.append(f"Mean error: {row['mean_error_mm']:.3f} mm")
        lines.append(f"Mean absolute error: {row['mean_absolute_error_mm']:.3f} mm")
        lines.append(f"RMSE: {row['rmse_mm']:.3f} mm")
        lines.append(f"Maximum absolute error: {row['max_absolute_error_mm']:.3f} mm")

    with open(output_report, "w") as file:
        file.write("\n".join(lines))

    return metrics_df



def create_manual_measurement_template(
    results_csv,
    output_csv,
    include_detected_only=True
):
    """
    Create a blank manual-measurement template from BioVisionLab results.

    The output CSV can be opened in Excel and filled in by a user.
    """

    results_csv = Path(results_csv)
    output_csv = Path(output_csv)

    results = pd.read_csv(results_csv)

    if "image" not in results.columns:
        raise ValueError("Results CSV must contain an 'image' column.")

    if include_detected_only and "detected" in results.columns:
        results = results[results["detected"] == True].copy()

    template = pd.DataFrame({
        "image": results["image"],
        "manual_gap_mm": "",
        "manual_left_width_mm": "",
        "manual_right_width_mm": "",
        "manual_left_growth_toward_mm": "",
        "manual_right_growth_toward_mm": "",
        "notes": ""
    })

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    template.to_csv(output_csv, index=False)

    return template
