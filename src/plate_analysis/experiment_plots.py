
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def _standard_error(values):
    values = pd.Series(values).dropna()

    if len(values) <= 1:
        return np.nan

    return values.std(ddof=1) / np.sqrt(len(values))


def plot_experiment_measurement(
    results_csv,
    output_plot,
    measurement="gap_mm",
    group_columns=None
):
    """
    Plot a BioVisionLab measurement over time.

    Examples:
    - gap_mm over day
    - left_width_mm over day
    - right_width_mm over day

    Optionally group by metadata columns such as:
    - cultivar
    - treatment
    - vl_isolate
    - lm_isolate
    """

    results_csv = Path(results_csv)
    output_plot = Path(output_plot)

    df = pd.read_csv(results_csv)

    if "detected" in df.columns:
        df = df[df["detected"] == True].copy()

    if len(df) == 0:
        raise ValueError("No detected images available for plotting.")

    if "day" not in df.columns:
        raise ValueError("Results CSV must contain a 'day' column.")

    if measurement not in df.columns:
        raise ValueError(f"Measurement column not found: {measurement}")

    df = df[df["day"].notna()].copy()
    df = df[df[measurement].notna()].copy()

    if len(df) == 0:
        raise ValueError("No usable rows available for plotting.")

    if group_columns is None:
        group_columns = []

    group_columns = [
        col for col in group_columns
        if col in df.columns and df[col].notna().any()
    ]

    output_plot.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))

    if len(group_columns) == 0:
        summary = df.groupby("day").agg(
            mean_value=(measurement, "mean"),
            se_value=(measurement, _standard_error),
            n_images=(measurement, "count")
        ).reset_index()

        plt.errorbar(
            summary["day"],
            summary["mean_value"],
            yerr=summary["se_value"],
            marker="o",
            capsize=4
        )

    else:
        df["group_label"] = df[group_columns].astype(str).agg(" | ".join, axis=1)

        summary = df.groupby(["group_label", "day"]).agg(
            mean_value=(measurement, "mean"),
            se_value=(measurement, _standard_error),
            n_images=(measurement, "count")
        ).reset_index()

        for group_label, group_df in summary.groupby("group_label"):
            group_df = group_df.sort_values("day")

            plt.errorbar(
                group_df["day"],
                group_df["mean_value"],
                yerr=group_df["se_value"],
                marker="o",
                capsize=4,
                label=group_label
            )

        plt.legend(fontsize=8)

    plt.xlabel("Day")
    plt.ylabel(measurement)
    plt.title(f"{measurement} over time")
    plt.tight_layout()
    plt.savefig(output_plot, dpi=300)
    plt.close()

    return summary
