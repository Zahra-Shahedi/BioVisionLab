
from pathlib import Path
import sys
import tempfile
import unittest
import cv2
import numpy as np

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.dataset_audit import audit_image_folder


class TestDatasetAudit(unittest.TestCase):

    def test_audit_image_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            image_dir = tmpdir / "images"
            output_csv = tmpdir / "audit.csv"
            output_report = tmpdir / "audit.txt"
            config_path = tmpdir / "config.json"

            image_dir.mkdir()

            img = np.zeros((600, 600, 3), dtype=np.uint8)
            cv2.circle(img, (300, 300), 240, (190, 190, 190), -1)
            cv2.circle(img, (300, 300), 240, (30, 30, 30), 4)

            cv2.imwrite(str(image_dir / "plate_001_day_3.png"), img)

            config_path.write_text(
                """{
                    "plate_diameter_mm": 90,
                    "threshold": 220,
                    "plate_radius_pixels": "auto",
                    "left_start_offset_x": -90,
                    "left_start_offset_y": 0,
                    "right_start_offset_x": 90,
                    "right_start_offset_y": 0
                }"""
            )

            audit = audit_image_folder(
                input_folder=image_dir,
                output_csv=output_csv,
                config_path=config_path,
                output_report=output_report
            )

            self.assertTrue(output_csv.exists())
            self.assertTrue(output_report.exists())
            self.assertEqual(len(audit), 1)
            self.assertTrue(bool(audit.iloc[0]["readable"]))


if __name__ == "__main__":
    unittest.main()
