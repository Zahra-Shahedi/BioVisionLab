
import cv2
import numpy as np


def _circle_mask(shape, center, radius):
    mask = np.zeros(shape, dtype=np.uint8)
    cv2.circle(mask, tuple(map(int, center)), int(radius), 255, -1)
    return mask


def keep_component_touching_seed(candidate_mask, center, search_radius, seed_radius, min_area_px=200):
    h, w = candidate_mask.shape

    search_mask = _circle_mask((h, w), center, search_radius)
    seed_mask = _circle_mask((h, w), center, seed_radius)

    local_mask = cv2.bitwise_and(candidate_mask, search_mask)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        local_mask,
        connectivity=8
    )

    output = np.zeros_like(candidate_mask)

    for label in range(1, num_labels):
        component = labels == label
        area = stats[label, cv2.CC_STAT_AREA]

        if area < min_area_px:
            continue

        touches_seed = np.any(component & (seed_mask > 0))

        if touches_seed:
            output[component] = 255

    return output


def make_seeded_colony_mask(
    gray,
    left_center,
    right_center,
    agar_center,
    colony_search_radius=190,
    seed_radius=35,
    agar_radius=90,
    gray_offset=8,
    contrast_offset=2,
    background_blur_size=151,
    open_kernel_size=3,
    close_kernel_size=9,
    min_area_px=200,
    plate_center=None,
    plate_radius=None,
    inner_plate_radius_factor=0.88
):
    """
    Segment dual-culture fungal colonies using expected colony seed locations.

    Optional rim exclusion:
    - If plate_center and plate_radius are provided, candidate pixels outside the inner plate
      are removed before component filtering.
    """

    x, y = map(int, agar_center)
    r = int(agar_radius)

    agar_roi = gray[y-r:y+r, x-r:x+r]

    if agar_roi.size == 0:
        raise ValueError("Agar reference region is empty. Check agar_center and agar_radius.")

    if background_blur_size % 2 == 0:
        background_blur_size += 1

    if background_blur_size < 3:
        background_blur_size = 3

    background = cv2.GaussianBlur(gray, (background_blur_size, background_blur_size), 0)
    contrast = cv2.subtract(gray, background)

    agar_contrast_roi = contrast[y-r:y+r, x-r:x+r]

    gray_threshold = np.percentile(agar_roi, 90) + gray_offset
    contrast_threshold = np.percentile(agar_contrast_roi, 95) + contrast_offset

    raw_candidate = (
        (gray > gray_threshold) |
        (contrast > contrast_threshold)
    ).astype("uint8") * 255

    # Exclude plastic rim before connected-component filtering
    if plate_center is not None and plate_radius is not None:
        inner_plate_mask = _circle_mask(
            gray.shape,
            plate_center,
            int(float(plate_radius) * float(inner_plate_radius_factor))
        )
        raw_candidate = cv2.bitwise_and(raw_candidate, inner_plate_mask)

    if open_kernel_size and open_kernel_size > 0:
        open_kernel = np.ones((int(open_kernel_size), int(open_kernel_size)), np.uint8)
        raw_candidate = cv2.morphologyEx(raw_candidate, cv2.MORPH_OPEN, open_kernel)

    left_mask = keep_component_touching_seed(
        raw_candidate,
        left_center,
        colony_search_radius,
        seed_radius,
        min_area_px=min_area_px
    )

    right_mask = keep_component_touching_seed(
        raw_candidate,
        right_center,
        colony_search_radius,
        seed_radius,
        min_area_px=min_area_px
    )

    final_mask = cv2.bitwise_or(left_mask, right_mask)

    if close_kernel_size and close_kernel_size > 0:
        close_kernel = np.ones((int(close_kernel_size), int(close_kernel_size)), np.uint8)
        final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_CLOSE, close_kernel)

    return final_mask
