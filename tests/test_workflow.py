
from pathlib import Path
import sys
import tempfile
import unittest
import cv2
import numpy as np

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.workflow import run_dual_culture_workflow


class TestWorkflow(unittest.TestCase):

    def test_full_workflow_mock_image(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            image_dir = tmpdir / "images"
            output_dir = tmpdir / "outputs"
            config_path = tmpdir / "config.json"

            image_dir.mkdir()

            img = np.zeros((600, 600, 3), dtype=np.uint8)
            cv2.circle(img, (300, 300), 240, (190, 190, 190), -1)
            cv2.circle(img, (300, 300), 240, (30, 30, 30), 4)
            cv2.circle(img, (210, 300), 40, (250, 250, 250), -1)
            cv2.circle(img, (390, 300), 35, (245, 245, 245), -1)

            image_path = image_dir / "plate_001_day_3.png"
            cv2.imwrite(str(image_path), img)

            config_path.write_text(
                """{
                    "plate_diameter_mm": 90,
                    "threshold": 220,
                    "plate_center_x": 300,
                    "plate_center_y": 300,
                    "plate_radius_pixels": 225,
                    "split_x": 300,
                    "left_start_x": 210,
                    "left_start_y": 300,
                    "right_start_x": 390,
                    "right_start_y": 300
                }"""
            )

            outputs = run_dual_culture_workflow(
                input_folder=image_dir,
                output_dir=output_dir,
                config_path=config_path,
                prefix="test",
                gap_min_mm=0,
                gap_max_mm=40
            )

            self.assertEqual(outputs["n_images"], 1)
            self.assertEqual(outputs["n_detected"], 1)
            self.assertTrue(outputs["results_csv"].exists())
            self.assertTrue(outputs["qc_csv"].exists())
            self.assertTrue(outputs["contact_sheet"].exists())
            self.assertTrue(outputs["report"].exists())


if __name__ == "__main__":
    unittest.main()
