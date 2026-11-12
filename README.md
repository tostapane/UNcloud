# UNcloud

Cloud removal on SEN12MS-CR: a U-Net that takes a cloudy Sentinel-2 image plus Sentinel-1 radar and predicts the clear image.

- `data.md`: data model (files, scaling, validity, split)
- `TODO.md`: architecture and data decisions
- `config.py`: shared constants

## Setup

Python 3.12. Pick one:

```bash
# uv (recommended)
uv sync

# venv + pip
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt

# conda
conda create -n uncloud python=3.12
conda activate uncloud
pip install -r requirements.txt
```

`uv.lock` pins exact versions; `requirements.txt` is generated from it for non-uv users.

## Changing dependencies

Edit `pyproject.toml` (or use `uv add <pkg>`), then regenerate both files:

```bash
uv lock
uv export --no-hashes -o requirements.txt
```

Commit `pyproject.toml`, `uv.lock` and `requirements.txt` together.
