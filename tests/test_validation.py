
from pathlib import Path
import sys
import tempfile
import unittest
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.validation import validate_gap_measurements


class TestValidation(unittest.TestCase):

    def test_gap_validation_metrics(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            results_csv = tmpdir / "results.csv"
            truth_csv = tmpdir / "truth.csv"
            output_csv = tmpdir / "validation.csv"
            output_plot = tmpdir / "validation.png"
            output_report = tmpdir / "validation.txt"

            results = pd.DataFrame({
                "image": ["plate_001_day_3.png", "plate_002_day_3.png"],
                "detected": [True, True],
                "gap_mm": [10.2, 19.8]
            })

            truth = pd.DataFrame({
                "image": ["plate_001_day_3.png", "plate_002_day_3.png"],
                "true_gap_mm": [10.0, 20.0]
            })

            results.to_csv(results_csv, index=False)
            truth.to_csv(truth_csv, index=False)

            metrics = validate_gap_measurements(
                results_csv=results_csv,
                ground_truth_csv=truth_csv,
                output_csv=output_csv,
                output_plot=output_plot,
                output_report=output_report
            )

            self.assertEqual(metrics["images_compared"], 2)
            self.assertAlmostEqual(metrics["mean_absolute_error_mm"], 0.2, places=3)
            self.assertTrue(output_csv.exists())
            self.assertTrue(output_plot.exists())
            self.assertTrue(output_report.exists())


if __name__ == "__main__":
    unittest.main()
