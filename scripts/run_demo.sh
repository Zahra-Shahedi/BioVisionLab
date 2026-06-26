#!/bin/bash

python scripts/analyze_dual_culture_folder.py \
    --input data/both_white_dual_culture \
    --output results/demo_results.csv \
    --annotated results/demo_annotated \
    --config config/dual_culture_mock.json \
    --plot results/demo_plot.png \
    --report results/demo_report.txt
