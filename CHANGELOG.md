# Changelog

All notable changes to BioVisionLab will be documented in this file.


## Unreleased

### Added

- Full dual-culture workflow command: `biovisionlab-run-workflow`.
- Manual measurement validation command.
- Manual measurement template command.
- QC flagging command.
- Experiment plotting command.
- CLI reference documentation.

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
