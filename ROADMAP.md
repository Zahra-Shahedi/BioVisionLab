# BioVisionLab roadmap

BioVisionLab is being developed as a practical biological image-analysis toolkit, starting with fungal dual-culture Petri dish assays.

## Current focus

The current version focuses on reproducible measurement of dual-culture fungal plate images.

It can:

- analyze folders of plate images
- detect colonies
- estimate colony width and gap
- create annotated QC images
- summarize measurements
- validate mock measurements against known ground truth
- generate contact sheets for rapid visual inspection

## Short-term goals

### Real-image testing

- Test the pipeline on real dual-culture plate photos.
- Adjust real-image config settings.
- Compare BioVisionLab measurements with manual measurements.
- Identify common failure cases.

### Improved segmentation

- Improve colony detection under uneven lighting.
- Add adaptive thresholding options.
- Add background correction.
- Add better handling for dark or low-contrast colonies.
- Add handling for merged or touching colonies.

### Quality control

- Add automatic flagging of suspicious measurements.
- Flag unusually large or small gaps.
- Flag images with low detection confidence.
- Save failed or suspicious images into a separate QC folder.

## Medium-term goals

### Biological experiment support

- Support treatment-level summaries.
- Support cultivar-level and isolate-level summaries.
- Export analysis-ready files for R.
- Add plots for growth over time by cultivar, treatment, and isolate pair.

### Real validation

- Compare automated measurements with manual measurements.
- Estimate measurement error.
- Report agreement between manual and automated measurements.
- Add validation plots for real experimental datasets.

## Long-term goals

### Machine learning and deep learning

Future versions may include machine learning or deep learning for:

- colony segmentation
- interaction classification
- contamination detection
- abnormal plate detection
- prediction of interaction outcomes from early growth images

## Possible future modules

BioVisionLab may later expand to:

- plant disease lesion measurement
- seed image analysis
- root image analysis
- microscopy image analysis
- field or greenhouse plant phenotyping images
