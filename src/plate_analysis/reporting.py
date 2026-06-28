
from pathlib import Path
import pandas as pd


def create_dual_culture_report(csv_path, report_path):
    """
    Create a text report from BioVisionLab dual-culture results.

    The report includes:
    - total images
    - detection rate
    - failed images
    - summary by day for successfully detected images
    """

    csv_path = Path(csv_path)
    report_path = Path(report_path)

    df = pd.read_csv(csv_path)

    total_images = len(df)

    if "detected" not in df.columns:
        raise ValueError("CSV must contain a 'detected' column.")

    detected_images = int(df["detected"].sum())
    failed_images = total_images - detected_images

    detection_rate = detected_images / total_images * 100 if total_images > 0 else 0

    detected_df = df[df["detected"] == True].copy()
    failed_df = df[df["detected"] == False].copy()

    lines = []

    lines.append("BioVisionLab Dual-Culture Analysis Report")
    lines.append("========================================")
    lines.append("")
    lines.append(f"Input results file: {csv_path.name}")
    lines.append(f"Total images analyzed: {total_images}")
    lines.append(f"Successfully detected: {detected_images}")
    lines.append(f"Failed detections: {failed_images}")
    lines.append(f"Detection rate: {detection_rate:.1f}%")
    lines.append("")

    if failed_images > 0:
        lines.append("Failed images")
        lines.append("-------------")

        for _, row in failed_df.iterrows():
            reason = row.get("failure_reason", "Unknown reason")
            lines.append(f"- {row['image']}: {reason}")

        lines.append("")

    if len(detected_df) > 0 and "day" in detected_df.columns:
        lines.append("Summary by day")
        lines.append("--------------")

        summary_by_day = detected_df.groupby("day").agg(
            n_images=("image", "count"),
            mean_left_width_mm=("left_width_mm", "mean"),
            mean_right_width_mm=("right_width_mm", "mean"),
            mean_gap_mm=("gap_mm", "mean"),
            mean_left_growth_toward_mm=("left_growth_toward_mm", "mean"),
            mean_right_growth_toward_mm=("right_growth_toward_mm", "mean")
        ).reset_index()

        for _, row in summary_by_day.iterrows():
            lines.append(
                f"Day {int(row['day'])}: "
                f"n={int(row['n_images'])}, "
                f"left width={row['mean_left_width_mm']:.2f} mm, "
                f"right width={row['mean_right_width_mm']:.2f} mm, "
                f"gap={row['mean_gap_mm']:.2f} mm"
            )

    else:
        lines.append("No successfully detected images available for summary.")

    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as file:
        file.write("\n".join(lines))

    return report_path
