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
