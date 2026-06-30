
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



def copy_qc_review_images(
    qc_csv,
    annotated_folder,
    output_folder,
    image_column="image"
):
    """
    Copy annotated images that have qc_flag == 'check' into a review folder.

    This helps users quickly inspect suspicious results.
    """

    import shutil

    qc_csv = Path(qc_csv)
    annotated_folder = Path(annotated_folder)
    output_folder = Path(output_folder)

    df = pd.read_csv(qc_csv)

    if "qc_flag" not in df.columns:
        raise ValueError("QC CSV must contain a 'qc_flag' column.")

    if image_column not in df.columns:
        raise ValueError(f"QC CSV must contain an '{image_column}' column.")

    output_folder.mkdir(parents=True, exist_ok=True)

    check_df = df[df["qc_flag"] == "check"].copy()

    copied = []
    missing = []

    for _, row in check_df.iterrows():
        original_name = row[image_column]
        stem = Path(original_name).stem

        possible_matches = list(annotated_folder.glob(f"{stem}*"))

        if len(possible_matches) == 0:
            missing.append(original_name)
            continue

        source = possible_matches[0]
        destination = output_folder / source.name

        shutil.copy2(source, destination)
        copied.append(destination.name)

    summary = {
        "n_flagged": len(check_df),
        "n_copied": len(copied),
        "n_missing": len(missing),
        "copied": copied,
        "missing": missing
    }

    return summary
