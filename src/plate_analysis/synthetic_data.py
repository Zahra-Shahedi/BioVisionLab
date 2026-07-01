
from pathlib import Path
import numpy as np
import cv2
import pandas as pd


def generate_mock_dual_culture_dataset(
    image_dir,
    ground_truth_csv,
    n_plates=10,
    days=None,
    image_size=600,
    plate_center=(300, 300),
    plate_radius_pixels=240,
    plate_diameter_mm=90,
    left_start=(210, 300),
    right_start=(390, 300),
    seed=42
):
    """
    Generate a mock dual-culture Petri dish image dataset.

    This is useful for demos, testing, and validation because the true gap
    between colonies is known.
    """

    image_dir = Path(image_dir)
    ground_truth_csv = Path(ground_truth_csv)

    image_dir.mkdir(parents=True, exist_ok=True)
    ground_truth_csv.parent.mkdir(parents=True, exist_ok=True)

    if days is None:
        days = [3, 5, 7, 10]

    pixels_per_mm = (plate_radius_pixels * 2) / plate_diameter_mm

    np.random.seed(seed)

    records = []

    for plate_id in range(1, n_plates + 1):
        for day in days:
            img = np.zeros((image_size, image_size, 3), dtype=np.uint8)

            cv2.circle(img, plate_center, plate_radius_pixels, (190, 190, 190), -1)
            cv2.circle(img, plate_center, plate_radius_pixels, (30, 30, 30), 4)

            radius_left = int(18 + day * 5 + np.random.randint(-2, 3))
            radius_right = int(16 + day * 4 + np.random.randint(-2, 3))

            cv2.circle(img, left_start, radius_left, (250, 250, 250), -1)
            cv2.circle(img, right_start, radius_right, (245, 245, 245), -1)

            filename = f"dual_white_plate_{plate_id:03d}_day_{day}.png"
            path = image_dir / filename
            cv2.imwrite(str(path), img)

            true_gap_mm = ((right_start[0] - radius_right) - (left_start[0] + radius_left)) / pixels_per_mm

            records.append({
                "image": filename,
                "plate_id": plate_id,
                "day": day,
                "true_left_radius_px": radius_left,
                "true_right_radius_px": radius_right,
                "true_gap_mm": true_gap_mm
            })

    truth = pd.DataFrame(records)
    truth.to_csv(ground_truth_csv, index=False)

    return {
        "image_dir": image_dir,
        "ground_truth_csv": ground_truth_csv,
        "n_images": len(truth),
        "dataframe": truth
    }
