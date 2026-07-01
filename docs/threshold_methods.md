# Threshold methods in BioVisionLab

BioVisionLab uses thresholding to separate fungal colony pixels from the background.

Different image conditions may require different threshold methods.

## Available methods

### 1. Global threshold

```json
"threshold_method": "global",
"threshold": 220

## Mask cleanup options

Real images may contain small bright artifacts such as dust, glare, agar texture, or label reflections. BioVisionLab includes optional mask cleanup settings.

### Opening

```json
"open_kernel_size": 3
```

Opening removes small bright noise from the fungal mask.

Use this when:

- tiny bright dots are detected as fungus
- agar texture creates small false-positive regions
- dust or glare specks appear in the mask

Recommended starting values:

```json
"open_kernel_size": 0
```

or:

```json
"open_kernel_size": 3
```

### Closing

```json
"close_kernel_size": 3
```

Closing fills small holes inside detected colonies.

Use this when:

- colony masks look broken
- small holes appear inside the colony region
- colony edges are fragmented

Recommended starting values:

```json
"close_kernel_size": 0
```

or:

```json
"close_kernel_size": 3
```

### Minimum colony area

```json
"min_colony_area_px": 50
```

This removes tiny detected objects before choosing the main colony contour.

Increase this value if small objects are being mistaken for colonies.

Recommended starting values:

```json
"min_colony_area_px": 50
```

or for larger images:

```json
"min_colony_area_px": 100
```

## Practical tuning order

For real images, tune settings in this order:

1. Choose `threshold_method`.
2. Adjust `threshold`, if using global threshold.
3. Add `open_kernel_size` if there is small bright noise.
4. Add `close_kernel_size` if colony masks have holes.
5. Increase `min_colony_area_px` if small false colonies are detected.
6. Check annotated images and QC contact sheet.
