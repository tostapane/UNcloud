"""Constants shared by data, model and evaluation. See data.md."""

PATCH = 256

SEASONS = ["ROIs1158_spring", "ROIs1868_summer", "ROIs1970_fall", "ROIs2017_winter"]

# Optical (Sentinel-2): 13 bands, in file order.
S2_BANDS = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B9", "B10", "B11", "B12"]
S2_CLIP = (0, 10000)  # clip, then divide by 10000
RGB = [3, 2, 1]  # B4, B3, B2
NIR, RED = 7, 3  # B8, B4 (for NDVI)

# Radar (Sentinel-1): 2 bands in dB, in file order.
S1_BANDS = ["VV", "VH"]
S1_CLIP = [(-25.0, 0.0), (-32.5, 0.0)]  # clip, then rescale each to [0, 1]

# Model interface: input is optical (0-12) then radar (13-14).
IN_CHANNELS = 15
OUT_CHANNELS = 13

# s2cloudless settings, same as the official loader.
S2CLOUDLESS = dict(threshold=0.4, average_over=4, dilation_size=2, all_bands=True)

# Split. A scene is its radar folder, e.g. "ROIs1158_spring_s1/s1_106".
# Match these exactly (scene in VAL), never by substring.
# Train is every scene in neither set: 155 scenes.
VAL = {
    "ROIs2017_winter_s1/s1_22",
    "ROIs1868_summer_s1/s1_19",
    "ROIs1970_fall_s1/s1_65",
    "ROIs1158_spring_s1/s1_17",
    "ROIs2017_winter_s1/s1_107",
    "ROIs1868_summer_s1/s1_80",
    "ROIs1868_summer_s1/s1_127",
    "ROIs2017_winter_s1/s1_130",
    "ROIs1868_summer_s1/s1_17",
    "ROIs2017_winter_s1/s1_84",
}
TEST = {
    "ROIs1158_spring_s1/s1_106",
    "ROIs1158_spring_s1/s1_123",
    "ROIs1158_spring_s1/s1_140",
    "ROIs1158_spring_s1/s1_31",
    "ROIs1158_spring_s1/s1_44",
    "ROIs1868_summer_s1/s1_119",
    "ROIs1868_summer_s1/s1_73",
    "ROIs1970_fall_s1/s1_139",
    "ROIs2017_winter_s1/s1_108",
    "ROIs2017_winter_s1/s1_63",
}
