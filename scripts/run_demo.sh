#!/bin/bash
set -e

echo "Generating mock dual-culture dataset..."
biovisionlab-generate-demo \
    --image-dir data/both_white_dual_culture \
    --ground-truth results/mock_dataset_ground_truth.csv \
    --n-plates 10 \
    --seed 42

echo "Running BioVisionLab full workflow..."
biovisionlab-run-workflow \
    --input data/both_white_dual_culture \
    --output-dir results \
    --config config/dual_culture_mock.json \
    --prefix demo \
    --gap-min-mm 0 \
    --gap-max-mm 40 \
    --plot-measurement gap_mm

echo "Validating BioVisionLab measurements against mock ground truth..."
biovisionlab-validate-mock
