from pathlib import Path
import numpy as np
import cv2
import pandas as pd


def main():
    project_dir = Path(__file__).resolve().parents[1]

    image_dir = project_dir / "data" / "both_white_dual_culture"
    results_dir = project_dir / "results"

    image_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    plate_center = (300, 300)
    plate_radius_pixels = 240
    plate_diameter_mm = 90
    pixels_per_mm = (plate_radius_pixels * 2) / plate_diameter_mm

    left_start = (210, 300)
    right_start = (390, 300)

    days = [3, 5, 7, 10]
    records = []

    np.random.seed(42)

    for plate_id in range(1, 11):
        for day in days:
            img = np.zeros((600, 600, 3), dtype=np.uint8)

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
    truth_path = results_dir / "mock_dataset_ground_truth.csv"
    truth.to_csv(truth_path, index=False)

    print("Mock dual-culture dataset generated.")
    print(f"Images saved at: {image_dir}")
    print(f"Ground truth saved at: {truth_path}")
    print(f"Images created: {len(truth)}")


if __name__ == "__main__":
    main()
