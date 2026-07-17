from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

from facetrust_benchmark.settings import ALLOWED_IMAGE_SUFFIXES, MAX_UPLOAD_BYTES


def safe_suffix(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    return suffix if suffix in ALLOWED_IMAGE_SUFFIXES else ".png"


def validate_image(path: Path) -> None:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Uploaded file is not a valid image.") from exc
    if width < 64 or height < 64:
        raise ValueError("Image must be at least 64x64.")
    if width * height > 36_000_000:
        raise ValueError("Image resolution is too large.")


def load_rgb(path: str | Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB"))


def copy_uploaded_image(source_path: Path, target_path: Path) -> str:
    if source_path.stat().st_size > MAX_UPLOAD_BYTES:
        raise ValueError("Image is larger than 16 MB.")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, target_path)
    validate_image(target_path)
    return target_path.name


def resize_for_metric(image: np.ndarray, size: int = 256) -> np.ndarray:
    pil = Image.fromarray(image.astype(np.uint8), mode="RGB")
    pil.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (size, size), "black")
    x = (size - pil.width) // 2
    y = (size - pil.height) // 2
    canvas.paste(pil, (x, y))
    return np.asarray(canvas)
