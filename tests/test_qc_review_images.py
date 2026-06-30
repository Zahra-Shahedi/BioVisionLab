
from pathlib import Path
import sys
import tempfile
import unittest
import pandas as pd
import cv2
import numpy as np

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.quality_control import copy_qc_review_images


class TestQCReviewImages(unittest.TestCase):

    def test_copy_qc_review_images(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            qc_csv = tmpdir / "qc.csv"
            annotated_dir = tmpdir / "annotated"
            output_dir = tmpdir / "review"

            annotated_dir.mkdir()

            qc = pd.DataFrame({
                "image": ["plate_001.png", "plate_002.png"],
                "qc_flag": ["check", "pass"],
                "qc_reason": ["gap_above_maximum", ""]
            })

            qc.to_csv(qc_csv, index=False)

            img = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2.imwrite(str(annotated_dir / "plate_001_annotated.png"), img)
            cv2.imwrite(str(annotated_dir / "plate_002_annotated.png"), img)

            summary = copy_qc_review_images(
                qc_csv=qc_csv,
                annotated_folder=annotated_dir,
                output_folder=output_dir
            )

            self.assertEqual(summary["n_flagged"], 1)
            self.assertEqual(summary["n_copied"], 1)
            self.assertTrue((output_dir / "plate_001_annotated.png").exists())
            self.assertFalse((output_dir / "plate_002_annotated.png").exists())


if __name__ == "__main__":
    unittest.main()
