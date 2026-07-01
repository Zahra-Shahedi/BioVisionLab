
from pathlib import Path
import sys
import tempfile
import unittest
import cv2
import numpy as np

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.mask_preview import create_mask_preview


class TestMaskPreview(unittest.TestCase):

    def test_create_mask_preview(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            image_path = tmpdir / "plate_001_day_3.png"
            config_path = tmpdir / "config.json"
            output_dir = tmpdir / "mask_preview"

            img = np.zeros((600, 600, 3), dtype=np.uint8)
            cv2.circle(img, (300, 300), 240, (190, 190, 190), -1)
            cv2.circle(img, (300, 300), 240, (30, 30, 30), 4)
            cv2.circle(img, (210, 300), 40, (250, 250, 250), -1)
            cv2.circle(img, (390, 300), 35, (245, 245, 245), -1)

            cv2.imwrite(str(image_path), img)

            config_path.write_text(
                """{
                    "plate_diameter_mm": 90,
                    "threshold": 220,
                    "threshold_method": "global",
                    "adaptive_block_size": 51,
                    "adaptive_c": 2,
                    "open_kernel_size": 0,
                    "close_kernel_size": 0,
                    "min_colony_area_px": 50,
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

            result = create_mask_preview(
                image_path=image_path,
                config_path=config_path,
                output_dir=output_dir
            )

            self.assertTrue(result["gray_path"].exists())
            self.assertTrue(result["mask_path"].exists())
            self.assertTrue(result["overlay_path"].exists())
            self.assertGreater(result["mask_area_px"], 0)


if __name__ == "__main__":
    unittest.main()
