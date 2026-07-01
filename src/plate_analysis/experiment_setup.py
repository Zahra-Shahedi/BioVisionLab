
from pathlib import Path
import json


def initialize_experiment_folder(
    output_dir,
    plate_diameter_mm=90,
    threshold=220,
    left_start_offset_x=-90,
    right_start_offset_x=90
):
    """
    Create a starter folder structure for a new BioVisionLab experiment.
    """

    output_dir = Path(output_dir)

    data_dir = output_dir / "data" / "raw_images"
    results_dir = output_dir / "results"
    config_dir = output_dir / "config"

    data_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "plate_diameter_mm": plate_diameter_mm,
        "threshold": threshold,
        "plate_radius_pixels": "auto",
        "left_start_offset_x": left_start_offset_x,
        "left_start_offset_y": 0,
        "right_start_offset_x": right_start_offset_x,
        "right_start_offset_y": 0
    }

    config_path = config_dir / "dual_culture_config.json"

    with open(config_path, "w") as file:
        json.dump(config, file, indent=4)

    readme_path = output_dir / "README_experiment.md"

    readme_lines = [
        "# BioVisionLab experiment folder",
        "",
        "This folder was created as a starter structure for a BioVisionLab dual-culture image-analysis experiment.",
        "",
        "## Folder structure",
        "",
        "- `data/raw_images/`: put original plate images here",
        "- `results/`: BioVisionLab outputs will be saved here",
        "- `config/dual_culture_config.json`: experiment-specific configuration file",
        "",
        "## Suggested image naming",
        "",
        "Use filenames that include isolate, cultivar, plate number, and day.",
        "",
        "Example:",
        "",
        "`VL243377_MB10-191A_Westar_plate_001_day_7.jpg`",
        "",
        "## Preflight audit",
        "",
        "Before running full analysis:",
        "",
        "```bash",
        "biovisionlab-audit-dataset \\",
        "    --input data/raw_images \\",
        "    --output results/dataset_audit.csv \\",
        "    --config config/dual_culture_config.json \\",
        "    --report results/dataset_audit_report.txt",
        "```",
        "",
        "## Config preview",
        "",
        "Check one image before batch analysis:",
        "",
        "```bash",
        "biovisionlab-preview-config \\",
        "    --image data/raw_images/example_image.jpg \\",
        "    --config config/dual_culture_config.json \\",
        "    --output results/config_preview.png",
        "```",
        "",
        "## Full workflow",
        "",
        "Run the full workflow:",
        "",
        "```bash",
        "biovisionlab-run-workflow \\",
        "    --input data/raw_images \\",
        "    --output-dir results \\",
        "    --config config/dual_culture_config.json \\",
        "    --prefix experiment \\",
        "    --gap-min-mm 0 \\",
        "    --plot-measurement gap_mm",
        "```",
        ""
    ]

    readme_path.write_text("\n".join(readme_lines))

    return {
        "output_dir": output_dir,
        "data_dir": data_dir,
        "results_dir": results_dir,
        "config_dir": config_dir,
        "config_path": config_path,
        "readme_path": readme_path
    }
