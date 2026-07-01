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

## 13. Compare threshold methods

Compares threshold methods on one image and saves annotated outputs for each method.

```bash
biovisionlab-compare-thresholds \
    --image data/both_white_dual_culture/dual_white_plate_001_day_10.png \
    --config config/dual_culture_mock.json \
    --output-dir results/threshold_comparison
```

By default, this compares:

- global threshold
- Otsu threshold
- adaptive threshold

You can also choose specific methods:

```bash
biovisionlab-compare-thresholds \
    --image data/raw_images/example_plate.jpg \
    --config config/dual_culture_config.json \
    --output-dir results/threshold_comparison \
    --methods global otsu
```

This is useful before batch analysis because it helps choose the best segmentation method for real plate images.

## 14. Preview fungus mask

Creates mask-preview outputs for one image so users can see what BioVisionLab detects as fungus.

```bash
biovisionlab-preview-mask \
    --image data/both_white_dual_culture/dual_white_plate_001_day_10.png \
    --config config/dual_culture_mock.json \
    --output-dir results/mask_preview
```

This saves:

- grayscale image
- binary fungus mask
- mask overlay on the original image

This is useful for debugging threshold and mask-cleanup settings before running full analysis.
