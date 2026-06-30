
from pathlib import Path
import sys
import tempfile
import unittest
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.quality_control import add_qc_flags


class TestQualityControl(unittest.TestCase):

    def test_qc_flags(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            results_csv = tmpdir / "results.csv"
            output_csv = tmpdir / "qc_results.csv"

            results = pd.DataFrame({
                "image": [
                    "good_plate.png",
                    "failed_plate.png",
                    "negative_gap_plate.png",
                    "large_gap_plate.png"
                ],
                "detected": [True, False, True, True],
                "left_width_mm": [10.0, None, 10.0, 10.0],
                "right_width_mm": [10.0, None, 10.0, 10.0],
                "gap_mm": [5.0, None, -1.0, 100.0]
            })

            results.to_csv(results_csv, index=False)

            qc = add_qc_flags(
                results_csv=results_csv,
                output_csv=output_csv,
                gap_min_mm=0,
                gap_max_mm=40
            )

            self.assertTrue(output_csv.exists())

            good = qc[qc["image"] == "good_plate.png"].iloc[0]
            failed = qc[qc["image"] == "failed_plate.png"].iloc[0]
            negative = qc[qc["image"] == "negative_gap_plate.png"].iloc[0]
            large = qc[qc["image"] == "large_gap_plate.png"].iloc[0]

            self.assertEqual(good["qc_flag"], "pass")
            self.assertEqual(failed["qc_flag"], "check")
            self.assertIn("failed_detection", failed["qc_reason"])
            self.assertIn("negative_gap_possible_overlap", negative["qc_reason"])
            self.assertIn("gap_above_maximum", large["qc_reason"])


if __name__ == "__main__":
    unittest.main()
