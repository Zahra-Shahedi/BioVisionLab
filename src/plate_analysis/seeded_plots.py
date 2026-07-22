
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def plot_seeded_results(csv_path, output_dir, day_column="day"):
    """
    Create plots from seeded dual-culture measurements.

    Outputs:
    - gap_over_time.png
    - directional_growth_over_time.png
    """

    csv_path = Path(csv_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)

    if "detected" in df.columns:
        df = df[df["detected"] == True]

    if day_column not in df.columns:
        raise ValueError(f"Day column not found: {day_column}")

    df = df.sort_values(day_column)

    outputs = {}

    if "gap_mm" in df.columns:
        gap_plot = output_dir / "gap_over_time.png"

        plt.figure(figsize=(6, 4))
        plt.plot(df[day_column], df["gap_mm"], marker="o")
        plt.xlabel("Day")
        plt.ylabel("Gap between colonies (mm)")
        plt.title("Gap between colonies over time")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(gap_plot, dpi=300)
        plt.close()

        outputs["gap_plot"] = gap_plot

    required_growth_cols = [
        "left_growth_toward_mm",
        "right_growth_toward_mm"
    ]

    if all(col in df.columns for col in required_growth_cols):
        growth_plot = output_dir / "directional_growth_over_time.png"

        plt.figure(figsize=(6, 4))
        plt.plot(
            df[day_column],
            df["left_growth_toward_mm"],
            marker="o",
            label="Left colony"
        )
        plt.plot(
            df[day_column],
            df["right_growth_toward_mm"],
            marker="o",
            label="Right colony"
        )
        plt.xlabel("Day")
        plt.ylabel("Growth toward opponent (mm)")
        plt.title("Directional growth toward opponent")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(growth_plot, dpi=300)
        plt.close()

        outputs["directional_growth_plot"] = growth_plot

    if not outputs:
        raise ValueError("No supported seeded measurement columns found for plotting.")

    return outputs
