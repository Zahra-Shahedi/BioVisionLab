# BioVisionLab command-line reference

After installing BioVisionLab from the project folder:

```bash
pip install -e .

## 11. Initialize a new experiment folder

Creates a clean folder structure for a new BioVisionLab experiment.

```bash
biovisionlab-init-experiment \
    --output-dir my_dual_culture_experiment
```

This creates:

- `data/raw_images/` for original plate images
- `results/` for BioVisionLab outputs
- `config/dual_culture_config.json` for experiment settings
- `README_experiment.md` with example commands

## 12. Generate a mock demo dataset

Creates synthetic dual-culture plate images with known ground-truth gap measurements.

```bash
biovisionlab-generate-demo \
    --image-dir data/both_white_dual_culture \
    --ground-truth results/mock_dataset_ground_truth.csv \
    --n-plates 10 \
    --seed 42
```

This is useful for:

- testing BioVisionLab
- demonstrating the workflow
- validating automated measurements against known ground truth
