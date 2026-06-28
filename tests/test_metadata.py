
from pathlib import Path
import sys
import unittest

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.metadata import parse_plate_metadata


class TestMetadataParsing(unittest.TestCase):

    def test_mock_filename(self):
        metadata = parse_plate_metadata("dual_white_plate_001_day_3.png")

        self.assertEqual(metadata["plate_id"], 1)
        self.assertEqual(metadata["day"], 3)

    def test_real_filename_with_isolates(self):
        metadata = parse_plate_metadata(
            "DAOMC243377_MB10-191A_45M35_plate_012_day_10.jpg"
        )

        self.assertEqual(metadata["vl_isolate"], "DAOMC243377")
        self.assertEqual(metadata["lm_isolate"], "MB10-191A")
        self.assertEqual(metadata["cultivar"], "45M35")
        self.assertEqual(metadata["plate_id"], 12)
        self.assertEqual(metadata["day"], 10)

    def test_treatment_filename(self):
        metadata = parse_plate_metadata(
            "CO2_MB10-083A_Westar_VLfirst_plate_003_day_5.jpg"
        )

        self.assertEqual(metadata["vl_isolate"], "CO2")
        self.assertEqual(metadata["lm_isolate"], "MB10-083A")
        self.assertEqual(metadata["cultivar"], "Westar")
        self.assertEqual(metadata["treatment"], "VL-first")
        self.assertEqual(metadata["plate_id"], 3)
        self.assertEqual(metadata["day"], 5)


if __name__ == "__main__":
    unittest.main()
