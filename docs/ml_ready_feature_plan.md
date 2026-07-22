# ML-ready feature plan for BioVisionLab

BioVisionLab is being developed as a biological image-analysis and phenotyping workflow for fungal dual-culture experiments.

The long-term goal is to convert plate images into reproducible quantitative traits that can support machine-learning analysis, model comparison, and biological interpretation.

## Connection to precision phenotyping workflows

Modern precision-agriculture studies often follow a pipeline:

1. collect sensing or image data,
2. preprocess and standardize the data,
3. derive biologically meaningful features,
4. train and compare machine-learning models,
5. evaluate predictions on held-out data,
6. interpret which features drive the model.

BioVisionLab follows the same logic at the laboratory-image scale.

Instead of UAV multispectral or LiDAR observations, BioVisionLab uses plate images.
Instead of vegetation indices or canopy structural metrics, BioVisionLab derives fungal colony traits such as growth, gap distance, pigmentation, texture, and edge structure.

## Current image-derived traits

The seeded segmentation workflow already extracts:

- left and right colony width,
- left and right colony height,
- colony area in pixels,
- gap between colonies,
- growth toward the opponent,
- annotated quality-control images.

These traits describe fungal growth and interaction dynamics over time.

## Planned ML-ready features

Future feature extraction should include additional colony-level descriptors:

### Morphology features

- colony area,
- colony width and height,
- circularity,
- edge irregularity,
- growth direction toward opponent,
- gap distance.

### Color and pigmentation features

- mean RGB values,
- mean HSV values,
- color intensity,
- pigmentation differences between left and right colonies.

These features can support pigmented fungi such as pink, gray, dark, or black colonies.

### Texture features

- texture contrast,
- texture entropy,
- local intensity variation,
- ring or zonation score.

These features are important for fuzzy, ringed, zonate, or irregular fungal colonies.

### Quality-control features

- detection success,
- segmentation area,
- rim-contact warning,
- low-contrast warning,
- possible over-segmentation or under-segmentation flags.

## Future ML tasks

BioVisionLab can later support machine-learning tasks such as:

1. classification of colony morphology type,
2. prediction of segmentation success or failure,
3. classification of interaction outcome,
4. prediction of later gap distance from earlier images,
5. automatic selection of the most appropriate segmentation method.

## Why this matters

This feature-based design makes BioVisionLab more than a segmentation script. It becomes a reproducible phenotyping workflow that converts biological images into structured data suitable for machine learning.

## Important limitation

Synthetic images can help stress-test segmentation and feature extraction, but real plate images are still needed for final validation. Synthetic data should be used as a benchmark and development tool, not as a replacement for real experimental validation.
