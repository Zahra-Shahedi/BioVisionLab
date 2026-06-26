
import re
from pathlib import Path


def parse_plate_metadata(filename):
    """
    Extract plate_id and day from image filename.

    Expected examples:
    dual_white_plate_001_day_3.png
    plate_001_day_10.jpg
    sample_plate_023_day_7.jpeg
    """

    name = Path(filename).stem

    plate_match = re.search(r"plate[_-](\d+)", name)
    day_match = re.search(r"day[_-](\d+)", name)

    metadata = {
        "plate_id": None,
        "day": None
    }

    if plate_match:
        metadata["plate_id"] = int(plate_match.group(1))

    if day_match:
        metadata["day"] = int(day_match.group(1))

    return metadata
