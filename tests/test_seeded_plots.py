
from pathlib import Path
import sys
import tempfile
import unittest
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.seeded_plots import plot_seeded_results


class TestSeededPlots(unittest.TestCase):

    def test_plot_seeded_results(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            csv_path = tmpdir / "seeded_measurements.csv"
            output_dir = tmpdir / "plots"

            df = pd.DataFrame({
                "day": [3, 5, 7],
                "detected": [True, True, True],
                "gap_mm": [35.0, 15.0, 3.0],
                "left_growth_toward_mm": [8.0, 18.0, 28.0],
                "right_growth_toward_mm": [7.0, 17.0, 29.0],
            })

            df.to_csv(csv_path, index=False)

            outputs = plot_seeded_results(
                csv_path=csv_path,
                output_dir=output_dir
            )

            self.assertIn("gap_plot", outputs)
            self.assertIn("directional_growth_plot", outputs)

            self.assertTrue(outputs["gap_plot"].exists())
            self.assertTrue(outputs["directional_growth_plot"].exists())


if __name__ == "__main__":
    unittest.main()
