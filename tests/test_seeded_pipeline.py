
from pathlib import Path
import sys
import tempfile
import unittest
import json
import cv2
import numpy as np
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.seeded_pipeline import analyze_seeded_folder


class TestSeededPipeline(unittest.TestCase):

    def test_seeded_pipeline_with_calibration_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            image_dir = tmpdir / "images"
            image_dir.mkdir()

            annotated_dir = tmpdir / "annotated"
            output_csv = tmpdir / "measurements.csv"
            config_path = tmpdir / "config.json"
            calibration_path = tmpdir / "calibration.csv"

            image_path = image_dir / "CO2_MB10-191A_Westar_VLfirst_plate_001_day_3.png"

            img = np.full((600, 600, 3), 120, dtype=np.uint8)

            # Plate background and rim
            cv2.circle(img, (300, 300), 260, (130, 130, 130), -1)
            cv2.circle(img, (300, 300), 260, (230, 230, 230), 8)

            # Colonies
            cv2.circle(img, (210, 300), 55, (245, 245, 245), -1)
            cv2.circle(img, (390, 300), 60, (250, 250, 250), -1)

            cv2.imwrite(str(image_path), img)

            config = {
                "plate_diameter_mm": 90,
                "plate_radius_pixels": 260,
                "split_x": 300,
                "left_start_x": 210,
                "left_start_y": 300,
                "right_start_x": 390,
                "right_start_y": 300,
                "agar_reference_x": 300,
                "agar_reference_y": 120,
                "colony_search_radius": 100,
                "seed_radius": 25,
                "agar_radius": 40,
                "gray_offset": 8,
                "contrast_offset": 2,
                "background_blur_size": 51,
                "open_kernel_size": 3,
                "close_kernel_size": 5,
                "min_colony_area_px": 100,
                "plate_center_x": 300,
                "plate_center_y": 300,
                "inner_plate_radius_factor": 0.85
            }

            config_path.write_text(json.dumps(config))

            calibration = pd.DataFrame([
                {
                    "image_name": image_path.name,
                    "left_start_x": 210,
                    "left_start_y": 300,
                    "right_start_x": 390,
                    "right_start_y": 300,
                    "agar_reference_x": 300,
                    "agar_reference_y": 120,
                    "split_x": 300,
                    "colony_search_radius": 100,
                    "seed_radius": 25,
                    "plate_center_x": 300,
                    "plate_center_y": 300,
                    "plate_radius_pixels": 260,
                    "inner_plate_radius_factor": 0.85
                }
            ])

            calibration.to_csv(calibration_path, index=False)

            df = analyze_seeded_folder(
                input_dir=image_dir,
                config_path=config_path,
                output_csv=output_csv,
                annotated_dir=annotated_dir,
                calibration_csv=calibration_path
            )

            self.assertTrue(output_csv.exists())
            self.assertEqual(len(df), 1)
            self.assertTrue(bool(df.loc[0, "detected"]))
            self.assertIn("left_growth_toward_mm", df.columns)
            self.assertIn("right_growth_toward_mm", df.columns)
            self.assertGreater(df.loc[0, "left_growth_toward_mm"], 0)
            self.assertGreater(df.loc[0, "right_growth_toward_mm"], 0)

            annotated_files = list(annotated_dir.glob("*.png"))
            self.assertEqual(len(annotated_files), 1)


if __name__ == "__main__":
    unittest.main()
