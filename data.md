# Data model

What the data part produces and what every other part of the project can rely on.
This was fixed before any data was downloaded. The items under "Left for the slice" are confirmed on the first few hundred samples.

## Raw files (as downloaded)

- Dataset: SEN12MS-CR, 122,218 samples, each a triplet of radar, cloudy optical and clear optical, all 256×256.
- Layout: `ROIs1158_spring_s1/s1_106/…tif`, with `s2` and `s2_cloudy` in place of `s1` for the other two files.
- Seasons: `ROIs1158_spring`, `ROIs1868_summer`, `ROIs1970_fall`, `ROIs2017_winter`.
- Radar file: 2 bands in dB, order VV, VH.
- Optical files: 13 bands of raw values, order B1, B2, B3, B4, B5, B6, B7, B8, B8A, B9, B10, B11, B12.

## Files we create

- Cloud probability: one 8-bit 256×256 file per sample, from s2cloudless on the cloudy image.
- Index: one row per sample (below).

## Index row

| Column | Meaning |
|---|---|
| ID | Season, scene number, patch number |
| Split | train, val or test |
| Paths | Radar, cloudy, clear, cloud probability |
| Coverage | Fraction of cloudy pixels |
| Invalid fractions | One each for radar, cloudy, clear |
| Keep | False for training samples with a blank or mostly invalid clear image |

Coverage uses the s2cloudless settings of the official loader: threshold 0.4, averaging 4, dilation 2, all bands.

## Sample (what the loader returns)

| Field | Shape | Type | Range |
|---|---|---|---|
| Cloudy optical | 13 × 256 × 256 | float32 | [0, 1] |
| Radar | 2 × 256 × 256 | float32 | [0, 1] |
| Clear optical | 13 × 256 × 256 | float32 | [0, 1] |
| Cloud probability | 1 × 256 × 256 | float32 | [0, 1] |
| Target validity | 1 × 256 × 256 | bool | — |
| Coverage | scalar | float32 | [0, 1] |
| ID | string | — | — |

## Scaling

- Optical: clip to [0, 10000], divide by 10000.
- Radar: clip VV to [−25, 0] and VH to [−32.5, 0], then rescale each to [0, 1].
- Invalid values: fill with 0 after scaling.

The radar ranges are the ones used by DSen2-CR and GLF-CR. The official loader's default clips both channels to [−25, 0]. Metrics are computed on the optical bands only, so this does not affect comparability.

## Validity

- Optical pixel: invalid if all 13 bands are exactly 0. This rule is provisional, see "Left for the slice".
- Radar pixel: invalid if it was NaN or infinite before filling.
- L1 loss: pixels where the clear image is invalid are excluded, using the target validity field.
- Cloud cross-entropy: pixels where the cloudy input is blank are excluded, because s2cloudless output is meaningless there. This is computed in the loss from the cloudy tensor (`cloudy.sum(0) == 0` per sample), with no extra field.

## Split

The official scene lists, matched by exact folder name: 155 training scenes, 10 validation, 10 test.

```python
VAL = [
    "ROIs2017_winter_s1/s1_22", "ROIs1868_summer_s1/s1_19", "ROIs1970_fall_s1/s1_65",
    "ROIs1158_spring_s1/s1_17", "ROIs2017_winter_s1/s1_107", "ROIs1868_summer_s1/s1_80",
    "ROIs1868_summer_s1/s1_127", "ROIs2017_winter_s1/s1_130", "ROIs1868_summer_s1/s1_17",
    "ROIs2017_winter_s1/s1_84",
]
TEST = [
    "ROIs1158_spring_s1/s1_106", "ROIs1158_spring_s1/s1_123", "ROIs1158_spring_s1/s1_140",
    "ROIs1158_spring_s1/s1_31", "ROIs1158_spring_s1/s1_44", "ROIs1868_summer_s1/s1_119",
    "ROIs1868_summer_s1/s1_73", "ROIs1970_fall_s1/s1_139", "ROIs2017_winter_s1/s1_108",
    "ROIs2017_winter_s1/s1_63",
]
```

- Training is the 155-scene list in the official loader (`SEN12MSCR` class in `data/dataLoader.py` of the UnCRtainTS repository). It should equal every scene not in the two lists above; check this on the full dataset.
- Exact matching is deliberate. The official loader filters by substring, so its training entry `s1_1` also matches `s1_106`, `s1_123` and `s1_140`, which puts 6 test scenes and 3 validation scenes into training. We do not reproduce that.
- A patch missing any of its three files is left out of the index.
- Broken samples are dropped from training only. Validation and test keep every sample, so the test set stays identical to the official one.

## Model interface

- Input: 15 channels, optical at 0–12 and radar at 13–14.
- Output: 13 optical bands in the same order, plus 1 cloud channel.
- Band indices: RGB is 3, 2, 1. NDVI uses 7 (B8) and 3 (B4).

## Left for the slice

- The exact file naming and file types.
- Radar channel order: confirm it is VV then VH. The second channel should look darker on average.
- Optical no-data pattern: count pixels where all bands are 0 and pixels where any band is 0. This decides the optical validity rule.
- The storage format of the mask files.
- The threshold for "mostly invalid".
- Whether a validity input channel is needed.
