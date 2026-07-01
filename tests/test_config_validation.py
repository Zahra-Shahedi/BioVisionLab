
from pathlib import Path
import sys
import tempfile
import unittest

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.config_validation import validate_config


class TestConfigValidation(unittest.TestCase):

    def test_valid_auto_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            config_path = tmpdir / "config.json"
            report_path = tmpdir / "report.txt"

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
                    "plate_radius_pixels": "auto",
                    "left_start_offset_x": -90,
                    "left_start_offset_y": 0,
                    "right_start_offset_x": 90,
                    "right_start_offset_y": 0
                }"""
            )

            result = validate_config(
                config_path=config_path,
                output_report=report_path
            )

            self.assertTrue(result["is_valid"])
            self.assertEqual(len(result["errors"]), 0)
            self.assertTrue(report_path.exists())

    def test_invalid_threshold_method(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            config_path = tmpdir / "bad_config.json"

            config_path.write_text(
                """{
                    "plate_diameter_mm": 90,
                    "threshold": 220,
                    "threshold_method": "wrong_method",
                    "plate_radius_pixels": "auto",
                    "left_start_offset_x": -90,
                    "left_start_offset_y": 0,
                    "right_start_offset_x": 90,
                    "right_start_offset_y": 0
                }"""
            )

            result = validate_config(config_path=config_path)

            self.assertFalse(result["is_valid"])
            self.assertGreater(len(result["errors"]), 0)


if __name__ == "__main__":
    unittest.main()
