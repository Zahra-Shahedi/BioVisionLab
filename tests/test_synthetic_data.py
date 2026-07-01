
from pathlib import Path
import sys
import tempfile
import unittest
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.synthetic_data import generate_mock_dual_culture_dataset


class TestSyntheticData(unittest.TestCase):

    def test_generate_mock_dual_culture_dataset(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            image_dir = tmpdir / "images"
            truth_csv = tmpdir / "ground_truth.csv"

            result = generate_mock_dual_culture_dataset(
                image_dir=image_dir,
                ground_truth_csv=truth_csv,
                n_plates=2,
                days=[3, 5],
                seed=42
            )

            self.assertTrue(image_dir.exists())
            self.assertTrue(truth_csv.exists())
            self.assertEqual(result["n_images"], 4)

            images = list(image_dir.glob("*.png"))
            self.assertEqual(len(images), 4)

            truth = pd.read_csv(truth_csv)
            self.assertIn("true_gap_mm", truth.columns)


if __name__ == "__main__":
    unittest.main()
