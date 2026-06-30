
from pathlib import Path
import sys
import tempfile
import unittest
import cv2
import numpy as np

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.pipeline import analyze_dual_culture_folder


class TestFailedImages(unittest.TestCase):

    def test_failed_image_is_copied(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            image_dir = tmpdir / "images"
            output_dir = tmpdir / "outputs"
            failed_dir = output_dir / "failed"
            config_path = tmpdir / "config.json"

            image_dir.mkdir()
            output_dir.mkdir()

            blank = np.zeros((600, 600, 3), dtype=np.uint8)
            image_path = image_dir / "plate_001_day_3.png"
            cv2.imwrite(str(image_path), blank)

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

            result = analyze_dual_culture_folder(
                input_folder=image_dir,
                output_csv=output_dir / "results.csv",
                annotated_folder=output_dir / "annotated",
                config_path=config_path,
                plot_path=output_dir / "plot.png",
                report_path=output_dir / "report.txt",
                failed_folder=failed_dir
            )

            df = result["dataframe"]

            self.assertEqual(len(df), 1)
            self.assertEqual(int(df["detected"].sum()), 0)
            self.assertTrue((failed_dir / "plate_001_day_3.png").exists())


if __name__ == "__main__":
    unittest.main()
