
from pathlib import Path
import sys
import tempfile
import unittest
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.experiment_plots import plot_experiment_measurement


class TestExperimentPlots(unittest.TestCase):

    def test_plot_experiment_measurement(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            results_csv = tmpdir / "results.csv"
            output_plot = tmpdir / "plot.png"

            results = pd.DataFrame({
                "image": [
                    "plate_001_day_3.png",
                    "plate_002_day_3.png",
                    "plate_003_day_5.png",
                    "plate_004_day_5.png"
                ],
                "detected": [True, True, True, True],
                "day": [3, 3, 5, 5],
                "cultivar": ["Westar", "Westar", "Westar", "Westar"],
                "gap_mm": [20.0, 22.0, 15.0, 17.0]
            })

            results.to_csv(results_csv, index=False)

            summary = plot_experiment_measurement(
                results_csv=results_csv,
                output_plot=output_plot,
                measurement="gap_mm",
                group_columns=["cultivar"]
            )

            self.assertTrue(output_plot.exists())
            self.assertEqual(len(summary), 2)


if __name__ == "__main__":
    unittest.main()
