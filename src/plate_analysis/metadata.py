
from pathlib import Path
import re


def parse_plate_metadata(filename):
    """
    Parse useful experiment metadata from a plate image filename.

    Supported examples:
    - dual_white_plate_001_day_3.png
    - plate_001_day_7.jpg
    - VL243377_LM191A_Westar_plate_001_day_7.jpg
    - DAOMC243377_MB10-191A_45M35_plate_012_day_10.jpg

    Returns a dictionary. Missing fields are returned as None.
    """

    stem = Path(filename).stem

    metadata = {
        "plate_id": None,
        "day": None,
        "vl_isolate": None,
        "lm_isolate": None,
        "cultivar": None,
        "treatment": None
    }

    # Plate number
    plate_match = re.search(r"plate[_-]?(\d+)", stem, flags=re.IGNORECASE)
    if plate_match:
        metadata["plate_id"] = int(plate_match.group(1))

    # Day number
    day_match = re.search(r"day[_-]?(\d+)", stem, flags=re.IGNORECASE)
    if day_match:
        metadata["day"] = int(day_match.group(1))

    # Split filename into useful parts
    tokens = re.split(r"[_\s]+", stem)

    known_cultivars = {
        "westar": "Westar",
        "45m35": "45M35"
    }

    known_treatments = {
        "control": "control",
        "dual": "dual",
        "single": "single",
        "lmfirst": "LM-first",
        "vlfirst": "VL-first",
        "lm-first": "LM-first",
        "vl-first": "VL-first"
    }

    known_vl_tokens = {
        "CO1", "CO2", "MB2", "MB4", "MB5", "MBCA001", "VL43"
    }

    for token in tokens:
        clean = token.strip()
        upper = clean.upper()
        lower = clean.lower()

        if lower in known_cultivars:
            metadata["cultivar"] = known_cultivars[lower]

        if lower in known_treatments:
            metadata["treatment"] = known_treatments[lower]

        # Verticillium longisporum isolate patterns
        if (
            upper.startswith("VL")
            or upper.startswith("DAOMC")
            or upper.startswith("CL")
            or upper in known_vl_tokens
        ):
            metadata["vl_isolate"] = clean

        # Leptosphaeria maculans isolate patterns
        if (
            upper.startswith("LM")
            or upper.startswith("MB10")
            or upper.startswith("BLG")
        ):
            metadata["lm_isolate"] = clean

    return metadata
