
from pathlib import Path
import sys
import tempfile
import unittest
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.manual_validation import create_manual_measurement_template


class TestManualTemplate(unittest.TestCase):

    def test_create_manual_measurement_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            results_csv = tmpdir / "results.csv"
            output_csv = tmpdir / "manual_template.csv"

            results = pd.DataFrame({
                "image": ["plate_001.png", "plate_002.png", "plate_003.png"],
                "detected": [True, False, True],
                "gap_mm": [10.0, None, 20.0]
            })

            results.to_csv(results_csv, index=False)

            template = create_manual_measurement_template(
                results_csv=results_csv,
                output_csv=output_csv,
                include_detected_only=True
            )

            self.assertTrue(output_csv.exists())
            self.assertEqual(len(template), 2)
            self.assertIn("manual_gap_mm", template.columns)
            self.assertIn("notes", template.columns)
            self.assertNotIn("plate_002.png", template["image"].tolist())


if __name__ == "__main__":
    unittest.main()
