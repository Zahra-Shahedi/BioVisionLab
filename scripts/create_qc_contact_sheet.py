
from pathlib import Path
import sys
import argparse

project_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(project_dir / "src"))

from plate_analysis.qc import create_contact_sheet


def main():
    parser = argparse.ArgumentParser(
        description="Create a QC contact sheet from annotated BioVisionLab images."
    )

    parser.add_argument("--input", required=True, help="Folder containing annotated images")
    parser.add_argument("--output", required=True, help="Path to save contact sheet image")
    parser.add_argument("--columns", type=int, default=4, help="Number of columns")
    parser.add_argument("--thumbnail-width", type=int, default=300, help="Thumbnail width in pixels")

    args = parser.parse_args()

    output_path = create_contact_sheet(
        image_folder=args.input,
        output_path=args.output,
        n_columns=args.columns,
        thumbnail_width=args.thumbnail_width
    )

    print("QC contact sheet created")
    print("------------------------")
    print(f"Saved at: {output_path}")


if __name__ == "__main__":
    main()
