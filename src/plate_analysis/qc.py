
from pathlib import Path
import cv2
import numpy as np


def create_contact_sheet(
    image_folder,
    output_path,
    n_columns=4,
    thumbnail_width=300,
    label_height=30
):
    """
    Create a contact sheet from annotated QC images.

    This helps users quickly inspect many analyzed plates in one image.
    """

    image_folder = Path(image_folder)
    output_path = Path(output_path)

    image_paths = sorted(
        list(image_folder.glob("*.png")) +
        list(image_folder.glob("*.jpg")) +
        list(image_folder.glob("*.jpeg"))
    )

    if len(image_paths) == 0:
        raise ValueError(f"No images found in {image_folder}")

    thumbnails = []

    for image_path in image_paths:
        img = cv2.imread(str(image_path))

        if img is None:
            continue

        height, width = img.shape[:2]
        scale = thumbnail_width / width
        thumbnail_height = int(height * scale)

        resized = cv2.resize(img, (thumbnail_width, thumbnail_height))

        label_strip = np.ones(
            (label_height, thumbnail_width, 3),
            dtype=np.uint8
        ) * 255

        cv2.putText(
            label_strip,
            image_path.name[:35],
            (5, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 0),
            1,
            cv2.LINE_AA
        )

        combined = np.vstack([label_strip, resized])
        thumbnails.append(combined)

    if len(thumbnails) == 0:
        raise ValueError("No readable images found.")

    thumb_height = thumbnails[0].shape[0]
    thumb_width = thumbnails[0].shape[1]

    n_images = len(thumbnails)
    n_rows = int(np.ceil(n_images / n_columns))

    sheet_height = n_rows * thumb_height
    sheet_width = n_columns * thumb_width

    sheet = np.ones((sheet_height, sheet_width, 3), dtype=np.uint8) * 255

    for i, thumb in enumerate(thumbnails):
        row = i // n_columns
        col = i % n_columns

        y_start = row * thumb_height
        x_start = col * thumb_width

        sheet[
            y_start:y_start + thumb_height,
            x_start:x_start + thumb_width
        ] = thumb

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), sheet)

    return output_path
