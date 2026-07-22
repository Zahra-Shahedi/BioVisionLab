
from pathlib import Path
import sys
import unittest
import cv2
import numpy as np

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.seeded_segmentation import make_seeded_colony_mask


class TestSeededSegmentation(unittest.TestCase):

    def test_seeded_segmentation_detects_two_colonies_and_ignores_rim(self):
        gray = np.full((600, 600), 120, dtype=np.uint8)

        # Bright plate rim artifact
        cv2.circle(gray, (300, 300), 260, 230, 8)

        # Two fungal colonies
        cv2.circle(gray, (210, 300), 55, 240, -1)
        cv2.circle(gray, (390, 300), 60, 245, -1)

        mask = make_seeded_colony_mask(
            gray=gray,
            left_center=(210, 300),
            right_center=(390, 300),
            agar_center=(300, 120),
            colony_search_radius=100,
            seed_radius=25,
            agar_radius=40,
            gray_offset=8,
            contrast_offset=2,
            background_blur_size=51,
            open_kernel_size=3,
            close_kernel_size=5,
            min_area_px=100,
            plate_center=(300, 300),
            plate_radius=260,
            inner_plate_radius_factor=0.85
        )

        self.assertGreater((mask > 0).sum(), 0)

        # Colonies should be detected
        self.assertEqual(mask[300, 210], 255)
        self.assertEqual(mask[300, 390], 255)

        # Rim should be excluded
        self.assertEqual(mask[40, 300], 0)


if __name__ == "__main__":
    unittest.main()
