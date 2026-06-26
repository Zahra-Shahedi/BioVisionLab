# BioVisionLab

BioVisionLab is a Python-based biological image-analysis toolkit.

The first module focuses on automated measurement of fungal dual-culture Petri dish assays. It was started to address a real research bottleneck: manually measuring fungal growth across hundreds or thousands of plate images.

## Why this project matters

Manual measurement of dual-culture plates can be slow, repetitive, and affected by user judgment. BioVisionLab aims to make this workflow faster, more reproducible, and easier to check.

## Current workflow

BioVisionLab currently takes:

- a folder of plate images
- an experiment configuration file

and produces:

- measurement CSV
- annotated quality-control images
- summary growth/gap plot
- text report

## Current measurements

The dual-culture module currently extracts:

- left colony width
- right colony width
- left colony growth toward the opposing colony
- right colony growth toward the opposing colony
- gap between colonies
- detection status for each image

## Run demo

From the project folder:

```bash
./scripts/run_demo.sh
