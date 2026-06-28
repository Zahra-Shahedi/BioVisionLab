
from pathlib import Path
import sys

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.validation import validate_gap_measurements


def main():
    metrics = validate_gap_measurements(
        results_csv=project_dir / "results" / "demo_results.csv",
        ground_truth_csv=project_dir / "results" / "mock_dataset_ground_truth.csv",
        output_csv=project_dir / "results" / "demo_validation.csv",
        output_plot=project_dir / "results" / "demo_validation_plot.png",
        output_report=project_dir / "results" / "demo_validation_report.txt"
    )

    print("BioVisionLab validation complete")
    print("--------------------------------")
    print(f"Images compared: {metrics['images_compared']}")
    print(f"Mean error: {metrics['mean_error_mm']:.3f} mm")
    print(f"Mean absolute error: {metrics['mean_absolute_error_mm']:.3f} mm")
    print(f"RMSE: {metrics['rmse_mm']:.3f} mm")
    print(f"Maximum absolute error: {metrics['max_absolute_error_mm']:.3f} mm")


if __name__ == "__main__":
    main()
