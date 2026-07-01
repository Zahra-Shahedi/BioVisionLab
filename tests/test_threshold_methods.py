
from pathlib import Path
import sys
import tempfile
import unittest
import cv2
import numpy as np

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.dual_culture import analyze_dual_culture_image


class TestThresholdMethods(unittest.TestCase):

    def test_global_and_otsu_thresholds(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            image_path = tmpdir / "plate_001_day_3.png"

            img = np.zeros((600, 600, 3), dtype=np.uint8)
            cv2.circle(img, (300, 300), 240, (190, 190, 190), -1)
            cv2.circle(img, (300, 300), 240, (30, 30, 30), 4)
            cv2.circle(img, (210, 300), 40, (250, 250, 250), -1)
            cv2.circle(img, (390, 300), 35, (245, 245, 245), -1)

            cv2.imwrite(str(image_path), img)

            for method in ["global", "otsu"]:
                result = analyze_dual_culture_image(
                    image_path=image_path,
                    pixels_per_mm=480 / 90,
                    threshold=220,
                    plate_center=(300, 300),
                    plate_radius=225,
                    split_x=300,
                    left_start=(210, 300),
                    right_start=(390, 300),
                    threshold_method=method
                )

                self.assertTrue(result["detected"])
                self.assertEqual(result["threshold_method"], method)
                self.assertIn("gap_mm", result)


if __name__ == "__main__":
    unittest.main()
