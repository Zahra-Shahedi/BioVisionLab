#!/bin/bash

echo "Generating mock dual-culture dataset..."
python scripts/generate_mock_dual_culture_dataset.py

echo "Running BioVisionLab analysis..."
python scripts/analyze_dual_culture_folder.py \
    --input data/both_white_dual_culture \
    --output results/demo_results.csv \
    --annotated results/demo_annotated \
    --config config/dual_culture_mock.json \
    --plot results/demo_plot.png \
    --report results/demo_report.txt


echo "Validating BioVisionLab measurements against mock ground truth..."
python scripts/validate_mock_demo.py


echo "Creating QC contact sheet..."
python scripts/create_qc_contact_sheet.py     --input results/demo_annotated     --output results/demo_qc_contact_sheet.png     --columns 4     --thumbnail-width 300
