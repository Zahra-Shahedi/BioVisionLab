
from pathlib import Path
import sys
import tempfile
import unittest
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.manual_validation import compare_with_manual_measurements


class TestManualValidation(unittest.TestCase):

    def test_compare_with_manual_measurements(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            results_csv = tmpdir / "results.csv"
            manual_csv = tmpdir / "manual.csv"
            output_csv = tmpdir / "manual_validation.csv"
            output_plot = tmpdir / "manual_validation.png"
            output_report = tmpdir / "manual_validation.txt"

            results = pd.DataFrame({
                "image": ["plate_001.png", "plate_002.png"],
                "detected": [True, True],
                "gap_mm": [10.0, 20.0],
                "left_width_mm": [5.0, 8.0]
            })

            manual = pd.DataFrame({
                "image": ["plate_001.png", "plate_002.png"],
                "manual_gap_mm": [11.0, 19.0],
                "manual_left_width_mm": [5.5, 7.5]
            })

            results.to_csv(results_csv, index=False)
            manual.to_csv(manual_csv, index=False)

            metrics = compare_with_manual_measurements(
                results_csv=results_csv,
                manual_csv=manual_csv,
                output_csv=output_csv,
                output_plot=output_plot,
                output_report=output_report
            )

            self.assertTrue(output_csv.exists())
            self.assertTrue(output_plot.exists())
            self.assertTrue(output_report.exists())
            self.assertEqual(len(metrics), 2)

            gap_metrics = metrics[metrics["measurement"] == "gap_mm"].iloc[0]
            self.assertAlmostEqual(gap_metrics["mean_absolute_error_mm"], 1.0, places=3)


if __name__ == "__main__":
    unittest.main()
