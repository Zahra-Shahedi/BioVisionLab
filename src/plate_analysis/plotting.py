
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def plot_dual_culture_summary(csv_path, output_path):
    """
    Create a summary plot of left colony width, right colony width,
    and gap between colonies over time.
    """

    csv_path = Path(csv_path)
    output_path = Path(output_path)

    df = pd.read_csv(csv_path)

    if "day" not in df.columns:
        raise ValueError("CSV must contain a 'day' column.")

    summary_by_day = df.groupby("day").agg(
        mean_left_width_mm=("left_width_mm", "mean"),
        mean_right_width_mm=("right_width_mm", "mean"),
        mean_gap_mm=("gap_mm", "mean"),
        n_images=("image", "count")
    ).reset_index()

    plt.figure(figsize=(8, 5))

    plt.plot(
        summary_by_day["day"],
        summary_by_day["mean_left_width_mm"],
        marker="o",
        label="Left colony width"
    )

    plt.plot(
        summary_by_day["day"],
        summary_by_day["mean_right_width_mm"],
        marker="o",
        label="Right colony width"
    )

    plt.plot(
        summary_by_day["day"],
        summary_by_day["mean_gap_mm"],
        marker="o",
        label="Gap between colonies"
    )

    plt.xlabel("Day")
    plt.ylabel("Measurement (mm)")
    plt.title("Dual-Culture Measurements Over Time")
    plt.legend()
    plt.grid(True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return summary_by_day
