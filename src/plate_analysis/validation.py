
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def validate_gap_measurements(results_csv, ground_truth_csv, output_csv, output_plot, output_report):
    """
    Compare BioVisionLab gap measurements against known ground truth values.

    This is mainly useful for mock datasets where true measurements are known.
    """

    results_csv = Path(results_csv)
    ground_truth_csv = Path(ground_truth_csv)
    output_csv = Path(output_csv)
    output_plot = Path(output_plot)
    output_report = Path(output_report)

    results = pd.read_csv(results_csv)
    truth = pd.read_csv(ground_truth_csv)

    merged = results.merge(truth, on="image", how="inner")

    if len(merged) == 0:
        raise ValueError("No matching image names found between results and ground truth.")

    merged = merged[merged["detected"] == True].copy()

    merged["gap_error_mm"] = merged["gap_mm"] - merged["true_gap_mm"]
    merged["absolute_gap_error_mm"] = merged["gap_error_mm"].abs()
    merged["squared_gap_error_mm"] = merged["gap_error_mm"] ** 2

    mean_error = merged["gap_error_mm"].mean()
    mean_absolute_error = merged["absolute_gap_error_mm"].mean()
    rmse = np.sqrt(merged["squared_gap_error_mm"].mean())
    max_absolute_error = merged["absolute_gap_error_mm"].max()

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_plot.parent.mkdir(parents=True, exist_ok=True)
    output_report.parent.mkdir(parents=True, exist_ok=True)

    merged.to_csv(output_csv, index=False)

    plt.figure(figsize=(6, 6))
    plt.scatter(merged["true_gap_mm"], merged["gap_mm"])

    min_value = min(merged["true_gap_mm"].min(), merged["gap_mm"].min())
    max_value = max(merged["true_gap_mm"].max(), merged["gap_mm"].max())

    plt.plot([min_value, max_value], [min_value, max_value], linestyle="--")
    plt.xlabel("True gap (mm)")
    plt.ylabel("BioVisionLab measured gap (mm)")
    plt.title("Gap measurement validation")
    plt.tight_layout()
    plt.savefig(output_plot, dpi=300)
    plt.close()

    lines = []
    lines.append("BioVisionLab Gap Measurement Validation")
    lines.append("======================================")
    lines.append("")
    lines.append(f"Results file: {results_csv.name}")
    lines.append(f"Ground truth file: {ground_truth_csv.name}")
    lines.append(f"Images compared: {len(merged)}")
    lines.append("")
    lines.append("Error metrics")
    lines.append("-------------")
    lines.append(f"Mean error: {mean_error:.3f} mm")
    lines.append(f"Mean absolute error: {mean_absolute_error:.3f} mm")
    lines.append(f"RMSE: {rmse:.3f} mm")
    lines.append(f"Maximum absolute error: {max_absolute_error:.3f} mm")
    lines.append("")
    lines.append("Interpretation")
    lines.append("--------------")
    lines.append("Mean error shows whether the method tends to overestimate or underestimate the gap.")
    lines.append("Mean absolute error shows the average size of the mistake.")
    lines.append("RMSE gives more weight to large mistakes.")
    lines.append("Maximum absolute error shows the worst individual case.")

    with open(output_report, "w") as file:
        file.write("\n".join(lines))

    return {
        "images_compared": len(merged),
        "mean_error_mm": mean_error,
        "mean_absolute_error_mm": mean_absolute_error,
        "rmse_mm": rmse,
        "max_absolute_error_mm": max_absolute_error
    }
