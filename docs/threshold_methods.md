# Threshold methods in BioVisionLab

BioVisionLab uses thresholding to separate fungal colony pixels from the background.

Different image conditions may require different threshold methods.

## Available methods

### 1. Global threshold

```json
"threshold_method": "global",
"threshold": 220
