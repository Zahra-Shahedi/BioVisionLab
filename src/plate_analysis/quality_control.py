
from pathlib import Path
import pandas as pd


def add_qc_flags(
    results_csv,
    output_csv,
    gap_min_mm=0,
    gap_max_mm=None
):
    """
    Add quality-control flags to BioVisionLab result rows.

    Flags include:
    - failed detection
    - missing measurements
    - negative gap
    - gap below minimum
    - gap above maximum
    """

    results_csv = Path(results_csv)
    output_csv = Path(output_csv)

    df = pd.read_csv(results_csv)

    qc_flags = []
    qc_reasons = []

    for _, row in df.iterrows():
        reasons = []

        detected = row.get("detected", True)

        if detected is False or str(detected).lower() == "false":
            reasons.append("failed_detection")

        required_columns = [
            "left_width_mm",
            "right_width_mm",
            "gap_mm"
        ]

        for col in required_columns:
            if col in df.columns and pd.isna(row.get(col)):
                reasons.append(f"missing_{col}")

        if "gap_mm" in df.columns and not pd.isna(row.get("gap_mm")):
            gap = row["gap_mm"]

            if gap < 0:
                reasons.append("negative_gap_possible_overlap")

            if gap < gap_min_mm:
                reasons.append("gap_below_minimum")

            if gap_max_mm is not None and gap > gap_max_mm:
                reasons.append("gap_above_maximum")

        if len(reasons) == 0:
            qc_flags.append("pass")
            qc_reasons.append("")
        else:
            qc_flags.append("check")
            qc_reasons.append("; ".join(reasons))

    df["qc_flag"] = qc_flags
    df["qc_reason"] = qc_reasons

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    return df
