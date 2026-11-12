# TODO

## Model architecture

### Backbone
- [ ] U-Net trained from scratch, five resolution levels: 256 → 128 → 64 → 32 → 16
- [ ] Widths 64 / 128 / 256 / 512 / 512, two residual blocks per level on the way down and on the way up
- [ ] Residual block: GroupNorm → SiLU → 3×3 convolution, twice, with a skip connection (no BatchNorm)
- [ ] Self-attention at the 32×32 and 16×16 levels
- [ ] Check the parameter count (about 65M, estimated)

### Input and outputs
- [ ] Input of 15 channels: 2 radar + 13 cloudy optical, concatenated
- [ ] Head 1: 13-band correction; training output is `cloudy + correction`
- [ ] Head 2: one-channel cloud probability, auxiliary output only
- [ ] Zero-initialise the last layer of the correction head, so the model starts as "copy the input"

### Loss
- [ ] L1 between the output and the clear image over all 13 bands
- [ ] Plus 0.01 × cross-entropy between the cloud head and the s2cloudless probability
- [ ] Exclude invalid pixels of the clear image from the L1 term
- [ ] Exclude pixels where the cloudy input is blank from the cross-entropy term (`cloudy.sum(0) == 0` per sample)

### Training (starting values, confirm in the smoke test)
- [ ] AdamW, peak learning rate 2e-4, warm-up, cosine decay, gradient clipping
- [ ] Mixed precision, batch size 16–32
- [ ] Exponential moving average of the weights
- [ ] Full 256×256 patches
- [ ] Set the schedule length from the measured pass time, aiming for 40–80 passes
- [ ] Regular checkpoints with resume
- [ ] Pick the final model on the validation split

### Inference
- [ ] Raw output: `cloudy + correction`, clamped to [0, 1]
- [ ] Faithful output: `(1 − mask) × cloudy + mask × raw`, so clear pixels pass through
- [ ] Ship the mask as a third output
- [ ] Average predictions over the eight flips and rotations

## Data decisions

### Dataset and channels
- [ ] SEN12MS-CR, full training split
- [ ] Keep all channels: radar VV and VH; optical in the order B1, B2, B3, B4, B5, B6, B7, B8, B8A, B9, B10, B11, B12
- [ ] Confirm on the slice that the radar order is VV then VH (the second channel should look darker on average)

### Normalisation
- [ ] Radar: clip VV to [−25, 0] and VH to [−32.5, 0], rescale each to [0, 1]
- [ ] Optical: clip to [0, 10000], divide by 10000

### Invalid pixels
- [ ] Fill invalid values with 0 after scaling (network input only)
- [ ] Compute validity in the loader: an optical pixel is invalid if all 13 bands are exactly 0 (provisional), a radar pixel if it was NaN or infinite before filling
- [ ] On the slice, count optical pixels with all bands 0 and with any band 0, then fix the optical validity rule
- [ ] Record the invalid fraction per sample (radar, cloudy, clear) during the s2cloudless pass
- [ ] Drop from training any sample whose clear target is blank or mostly invalid
- [ ] Count invalid pixels on the slice, then on the full dataset: NaN and infinite values, radar pixels at or below the clip minimum, optical pixels with all bands 0, fully blank patches, and how concentrated they are
- [ ] Use the count to set the drop threshold, and add a validity input channel only if invalid input pixels are widespread

### Cloud masks
- [ ] Run s2cloudless once on every cloudy image, store the probability as an 8-bit file per sample
- [ ] Compute a coverage fraction per sample with the official settings (threshold 0.4, averaging 4, dilation 2)
- [ ] No shadow mask: document shadows as a limit of the faithful output

### Split
- [ ] Use the official loader's region lists: 10 validation scenes, 10 test scenes
- [ ] Match folder names exactly (not by substring)
- [ ] Check that no test folder ends up in training

### Augmentation
- [ ] Flips and 90° rotations only, applied identically to radar, optical, target and mask

### Storage
- [ ] Download the archives onto the cloud volume, extract, delete each archive afterwards
- [ ] Train from the TIFFs if the loader timing allows, otherwise convert once
- [ ] Copy the data to the GPU pod's local NVMe before training

### Evaluation
- [ ] Official metrics code, all 13 bands on the [0, 1] scale: PSNR, SSIM, SAM, MAE
- [ ] Headline numbers computed the official way, with invalid pixels included; report the numbers with invalid pixels excluded next to them
- [ ] Report both the raw and the faithful output
- [ ] Results by coverage in five 20% bins
- [ ] Results on cloudy versus clear pixels
- [ ] NDVI error as the downstream measure
- [ ] Zero-training baseline: cloudy input as output
- [ ] Compare against the published numbers on the benchmark page
