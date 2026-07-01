
from pathlib import Path
import sys
import tempfile
import unittest
import cv2
import numpy as np

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.dual_culture import analyze_dual_culture_image


class TestMaskCleanup(unittest.TestCase):

    def test_small_noise_does_not_prevent_detection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            image_path = tmpdir / "noisy_plate_001_day_3.png"

            img = np.zeros((600, 600, 3), dtype=np.uint8)
            cv2.circle(img, (300, 300), 240, (190, 190, 190), -1)
            cv2.circle(img, (300, 300), 240, (30, 30, 30), 4)

            cv2.circle(img, (210, 300), 40, (250, 250, 250), -1)
            cv2.circle(img, (390, 300), 35, (245, 245, 245), -1)

            # Add tiny bright noise dots.
            for x, y in [(120, 120), (500, 150), (280, 500), (450, 450)]:
                cv2.circle(img, (x, y), 2, (255, 255, 255), -1)

            cv2.imwrite(str(image_path), img)

            result = analyze_dual_culture_image(
                image_path=image_path,
                pixels_per_mm=480 / 90,
                threshold=220,
                plate_center=(300, 300),
                plate_radius=225,
                split_x=300,
                left_start=(210, 300),
                right_start=(390, 300),
                threshold_method="global",
                open_kernel_size=3,
                close_kernel_size=0,
                min_colony_area_px=100
            )

            self.assertTrue(result["detected"])
            self.assertIn("gap_mm", result)
            self.assertEqual(result["open_kernel_size"], 3)
            self.assertEqual(result["min_colony_area_px"], 100)


if __name__ == "__main__":
    unittest.main()
