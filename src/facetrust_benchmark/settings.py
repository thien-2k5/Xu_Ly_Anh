from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PACKAGE_DIR.parents[1]
STATIC_DIR = PACKAGE_DIR / "static"
DETECTOR_MODEL_PATH = PROJECT_DIR / "models" / "deepfake_detector.pt"
COMMUNITY_FORENSICS_DIR = PROJECT_DIR / "models" / "hf" / "owenslab-commfor-model-384"
TRICLASS_DETECTOR_DIR = (
    PROJECT_DIR / "models" / "hf" / "prithivmlmods-ai-vs-deepfake-vs-real"
)
FACE_FORGERY_DETECTOR_DIR = (
    PROJECT_DIR / "models" / "hf" / "koreapeter-ms-eff-gcvit-b0-ffpp"
)

ALLOWED_IMAGE_SUFFIXES = {".jfif", ".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD_BYTES = 16 * 1024 * 1024
