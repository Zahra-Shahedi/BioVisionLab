# Changelog

All notable changes to BioVisionLab will be documented in this file.


## Unreleased

### Added

- Seeded result plotting command: `biovisionlab-plot-seeded`.

- Seeded colony segmentation workflow for difficult dual-culture plate images.

- Threshold method options for colony segmentation: global, Otsu, and adaptive.
- Threshold comparison command: `biovisionlab-compare-thresholds`.
- Mask preview command: `biovisionlab-preview-mask`.
- Config validation command: `biovisionlab-validate-config`.
- Mask cleanup options for noisy images: opening, closing, and minimum colony area.

### Added

- Full dual-culture workflow command: `biovisionlab-run-workflow`.
- Manual measurement validation command.
- Manual measurement template command.
- QC flagging command.
- Experiment plotting command.
- CLI reference documentation.






## v0.5.1 - Packaging and cleanup patch

### Fixed

- Tracked the threshold comparison module in version control.
- Removed temporary pilot configuration files from the working tree.
- Confirmed the repository is clean and tests pass after the seeded segmentation release.

## v0.5.0 - Seeded colony segmentation workflow

### Added

- Seeded colony segmentation workflow for difficult dual-culture plate images.
- Command: `biovisionlab-analyze-seeded`.
- Optional per-image calibration CSV for seed coordinates, agar reference points, split position, search radius, seed radius, and rim-exclusion settings.
- Rim-exclusion support using inner plate masks.
- Directional growth measurements toward the opponent:
  - `left_growth_toward_mm`
  - `right_growth_toward_mm`
- Annotated seeded-analysis quality-control images.
- Template config file: `config/seeded_dual_culture_template.json`.
- Template calibration file: `config/seeded_image_calibration_template.csv`.
- Automated tests for seeded segmentation and seeded pipeline analysis.

## v0.4.0 - Real-image segmentation and configuration tools

### Added

- Threshold method options for colony segmentation:
  - global threshold
  - Otsu threshold
  - adaptive threshold
- Mask cleanup options for noisy real images:
  - opening
  - closing
  - minimum colony area filtering
- Threshold comparison command: `biovisionlab-compare-thresholds`.
- Mask preview command: `biovisionlab-preview-mask`.
- Config validation command: `biovisionlab-validate-config`.
- Documentation for threshold methods, mask cleanup, mask preview, and config validation.
- Additional automated tests for threshold methods, mask cleanup, mask preview, threshold comparison, and config validation.

## v0.3.0 - Experiment setup and demo workflow improvements

### Added

- Experiment folder initialization command: `biovisionlab-init-experiment`.
- Demo dataset generation command: `biovisionlab-generate-demo`.
- Cleaner demo workflow using installed command-line tools.
- Experiment starter README generated automatically for new projects.
- Documentation for experiment initialization and demo data generation.
- Additional automated tests for experiment setup and synthetic demo data generation.

## v0.2.0 - Workflow, QC, and validation expansion

### Added

- One-command full dual-culture workflow: `biovisionlab-run-workflow`.
- Dataset audit / preflight command: `biovisionlab-audit-dataset`.
- Experiment folder initialization command: `biovisionlab-init-experiment`.
- Demo dataset generation command: `biovisionlab-generate-demo`.
- QC flagging command: `biovisionlab-qc-flags`.
- QC review-image export command: `biovisionlab-qc-review-images`.
- Failed-image QC folder support.
- Manual measurement template command.
- Manual-vs-automated validation command.
- Experiment plotting command.
- Experiment summary command.
- Config preview command.
- CLI reference documentation.
- Additional automated tests for workflow, QC, plotting, manual validation, failed images, and dataset audit.

## v0.1.0 - Initial research-tool release

### Added

- Dual-culture Petri dish image analysis pipeline.
- Mock dual-culture dataset generator.
- Measurement CSV output.
- Annotated quality-control images.
- Growth and gap summary plot.
- Text report generation.
- Automatic Petri dish detection option.
- Real-image configuration template.
- Real-image photography and organization protocol.
- Mock measurement validation against ground truth.
- QC contact sheet generation.
- Filename metadata parsing for isolates, cultivar, treatment, plate number, and day.
- Automated tests.
- GitHub Actions test workflow.
- Installable Python package structure using `pyproject.toml`.
- Command-line tools:
  - `biovisionlab-analyze`
  - `biovisionlab-contact-sheet`
  - `biovisionlab-validate-mock`
  - `biovisionlab-preview-config`
  - `biovisionlab-summarize`
- Experimental summary table generation.
