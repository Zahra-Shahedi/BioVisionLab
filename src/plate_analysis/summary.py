
from pathlib import Path
import pandas as pd
import numpy as np


def _standard_error(values):
    values = pd.Series(values).dropna()

    if len(values) <= 1:
        return np.nan

    return values.std(ddof=1) / np.sqrt(len(values))


def create_experiment_summary(
    results_csv,
    output_csv,
    group_columns=None
):
    """
    Create grouped summary statistics from BioVisionLab results.

    By default, the function groups by useful metadata columns when available:
    - vl_isolate
    - lm_isolate
    - cultivar
    - treatment
    - day
    """

    results_csv = Path(results_csv)
    output_csv = Path(output_csv)

    df = pd.read_csv(results_csv)

    if "detected" in df.columns:
        df = df[df["detected"] == True].copy()

    if len(df) == 0:
        raise ValueError("No detected images available for summary.")

    default_group_columns = [
        "vl_isolate",
        "lm_isolate",
        "cultivar",
        "treatment",
        "day"
    ]

    if group_columns is None:
        group_columns = []

        for col in default_group_columns:
            if col in df.columns and df[col].notna().any():
                group_columns.append(col)

    if len(group_columns) == 0:
        raise ValueError("No grouping columns were found.")

    measurement_columns = [
        "left_width_mm",
        "right_width_mm",
        "left_growth_toward_mm",
        "right_growth_toward_mm",
        "gap_mm"
    ]

    measurement_columns = [
        col for col in measurement_columns
        if col in df.columns
    ]

    summary_parts = []

    grouped = df.groupby(group_columns, dropna=False)

    for group_values, group_df in grouped:
        if not isinstance(group_values, tuple):
            group_values = (group_values,)

        row = {}

        for col, value in zip(group_columns, group_values):
            row[col] = value

        row["n_images"] = len(group_df)

        for measurement in measurement_columns:
            row[f"mean_{measurement}"] = group_df[measurement].mean()
            row[f"sd_{measurement}"] = group_df[measurement].std(ddof=1)
            row[f"se_{measurement}"] = _standard_error(group_df[measurement])

        summary_parts.append(row)

    summary = pd.DataFrame(summary_parts)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_csv, index=False)

    return summary
