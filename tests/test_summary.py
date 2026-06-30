
from pathlib import Path
import sys
import tempfile
import unittest
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.summary import create_experiment_summary


class TestExperimentSummary(unittest.TestCase):

    def test_summary_by_day(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            results_csv = tmpdir / "results.csv"
            output_csv = tmpdir / "summary.csv"

            results = pd.DataFrame({
                "image": [
                    "plate_001_day_3.png",
                    "plate_002_day_3.png",
                    "plate_003_day_5.png"
                ],
                "detected": [True, True, True],
                "day": [3, 3, 5],
                "gap_mm": [10.0, 12.0, 20.0],
                "left_width_mm": [5.0, 7.0, 9.0],
                "right_width_mm": [6.0, 8.0, 10.0]
            })

            results.to_csv(results_csv, index=False)

            summary = create_experiment_summary(
                results_csv=results_csv,
                output_csv=output_csv,
                group_columns=["day"]
            )

            self.assertEqual(len(summary), 2)
            self.assertTrue(output_csv.exists())

            day3 = summary[summary["day"] == 3].iloc[0]
            self.assertEqual(day3["n_images"], 2)
            self.assertAlmostEqual(day3["mean_gap_mm"], 11.0, places=3)


if __name__ == "__main__":
    unittest.main()
