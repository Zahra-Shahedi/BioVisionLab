
from pathlib import Path
import sys
import tempfile
import unittest
import json

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.experiment_setup import initialize_experiment_folder


class TestExperimentSetup(unittest.TestCase):

    def test_initialize_experiment_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            result = initialize_experiment_folder(
                output_dir=tmpdir / "experiment",
                plate_diameter_mm=90,
                threshold=220
            )

            self.assertTrue(result["data_dir"].exists())
            self.assertTrue(result["results_dir"].exists())
            self.assertTrue(result["config_dir"].exists())
            self.assertTrue(result["config_path"].exists())
            self.assertTrue(result["readme_path"].exists())

            with open(result["config_path"], "r") as file:
                config = json.load(file)

            self.assertEqual(config["plate_diameter_mm"], 90)
            self.assertEqual(config["threshold"], 220)
            self.assertEqual(config["plate_radius_pixels"], "auto")


if __name__ == "__main__":
    unittest.main()
