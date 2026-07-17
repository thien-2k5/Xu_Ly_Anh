from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import timm
import torch
from huggingface_hub import HfApi, hf_hub_download
from PIL import Image
from safetensors.torch import load_file
from torch import nn
from torchvision import transforms
from transformers import AutoImageProcessor, AutoModelForImageClassification

PROJECT_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_DIR / "models" / "hf" / "prithivmlmods-ai-vs-deepfake-vs-real"
COMMFOR_PATH = (
    PROJECT_DIR
    / "models"
    / "hf"
    / "owenslab-commfor-model-384"
    / "model.safetensors"
)
DATASET_ID = "Hemg/AI-Generated-vs-Real-Images-Datasets"
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

FAKE_INCLUDE = (
    "face",
    "portrait",
    "woman",
    "girl",
    "celeb",
    "biden",
    "trump",
    "human",
    "historical",
)
FAKE_EXCLUDE = (
    "logo",
    "interface",
    "quiz",
    "group",
    "collage",
    "cat",
    "animal",
    "generator",
    "banner",
)
REAL_INCLUDE = (
    "portrait",
    "female-face",
    "girl",
    "man",
    "woman",
    "celeb",
    "dwayne",
    "michael_b",
    "jennifer",
    "ferrera",
    "lindsay",
    "larajade",
    "black_and_white",
    "self-portrait",
    "child-face",
    "yousuf",
    "trump",
    "obama",
)
REAL_EXCLUDE = (
    "painting",
    "illustration",
    "magazine",
    "icon",
    "report",
    "collage",
    "group",
    "people",
    "cover",
    "vector",
    "draw",
    "statue",
    "book",
    "van-gogh",
    "pearl-earring",
    "bob-ross",
    "shelley-newman",
    "71l0xx",
)


class CommunityForensicsDetector(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.vit = timm.create_model(
            "vit_small_patch16_384.augreg_in21k_ft_in1k",
            pretrained=False,
        )
        self.vit.head = nn.Linear(384, 1)

    def forward(self, tensor: torch.Tensor) -> torch.Tensor:
        return self.vit(tensor)


def select_paths() -> tuple[list[str], list[str]]:
    files = [item.rfilename for item in HfApi().dataset_info(DATASET_ID).siblings]
    fake = filter_paths(
        files,
        prefix="AiArtData/AiArtData/",
        include=FAKE_INCLUDE,
        exclude=FAKE_EXCLUDE,
    )
    real = filter_paths(
        files,
        prefix="RealArt/RealArt/",
        include=REAL_INCLUDE,
        exclude=REAL_EXCLUDE,
    )
    return stable_sample(fake, 40), stable_sample(real, 40)


def filter_paths(
    files: list[str],
    *,
    prefix: str,
    include: tuple[str, ...],
    exclude: tuple[str, ...],
) -> list[str]:
    return [
        path
        for path in files
        if path.startswith(prefix)
        and path.lower().endswith(IMAGE_EXTENSIONS)
        and any(token in path.lower() for token in include)
        and not any(token in path.lower() for token in exclude)
    ]


def stable_sample(paths: list[str], count: int) -> list[str]:
    ranked = sorted(paths, key=lambda path: hashlib.sha256(path.encode()).hexdigest())
    if len(ranked) < count:
        raise RuntimeError(f"Need {count} images, found {len(ranked)}")
    return ranked[:count]


def download_images(directory: Path, paths: list[str]) -> list[Path]:
    local_paths: list[Path] = []
    for path in paths:
        local_paths.append(
            Path(
                hf_hub_download(
                    repo_id=DATASET_ID,
                    repo_type="dataset",
                    filename=path,
                    local_dir=directory,
                )
            )
        )
    return local_paths


def predict_triclass(paths: list[Path]) -> np.ndarray:
    processor = AutoImageProcessor.from_pretrained(MODEL_DIR, local_files_only=True)
    model = AutoModelForImageClassification.from_pretrained(MODEL_DIR, local_files_only=True)
    model.eval()
    scores: list[float] = []
    for start in range(0, len(paths), 8):
        images = []
        for path in paths[start : start + 8]:
            with Image.open(path) as image:
                images.append(image.convert("RGB"))
        inputs = processor(images=images, return_tensors="pt")
        with torch.inference_mode():
            probabilities = model(**inputs).logits.softmax(dim=1)
        scores.extend((probabilities[:, 0] + probabilities[:, 1]).tolist())
    return np.asarray(scores, dtype=np.float64)


def predict_community_forensics(paths: list[Path]) -> np.ndarray:
    model = CommunityForensicsDetector()
    model.load_state_dict(load_file(COMMFOR_PATH))
    model.eval()
    transform = transforms.Compose(
        [
            transforms.Resize(440, antialias=True),
            transforms.CenterCrop(384),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225),
            ),
        ]
    )
    scores: list[float] = []
    for start in range(0, len(paths), 8):
        images = []
        for path in paths[start : start + 8]:
            with Image.open(path) as image:
                images.append(transform(image.convert("RGB")))
        batch = torch.stack(images)
        with torch.inference_mode():
            scores.extend(model(batch).sigmoid().flatten().tolist())
    return np.asarray(scores, dtype=np.float64)


def balanced_accuracy(labels: np.ndarray, scores: np.ndarray, threshold: float) -> float:
    predictions = scores >= threshold
    fake_recall = float(np.mean(predictions[labels == 1]))
    real_recall = float(np.mean(~predictions[labels == 0]))
    return (fake_recall + real_recall) / 2


def select_threshold(labels: np.ndarray, scores: np.ndarray) -> float:
    candidates = np.linspace(0.35, 0.85, 101)
    return float(
        max(
            candidates,
            key=lambda value: (balanced_accuracy(labels, scores, value), -abs(value - 0.5)),
        )
    )


def summarize(name: str, labels: np.ndarray, scores: np.ndarray, threshold: float) -> None:
    predictions = scores >= threshold
    tp = int(np.sum((labels == 1) & predictions))
    fn = int(np.sum((labels == 1) & ~predictions))
    fp = int(np.sum((labels == 0) & predictions))
    tn = int(np.sum((labels == 0) & ~predictions))
    accuracy = float(np.mean(predictions == labels))
    fake_recall = tp / (tp + fn)
    real_recall = tn / (tn + fp)
    print(
        f"{name}: threshold={threshold:.3f} accuracy={accuracy:.3f} "
        f"balanced={(fake_recall + real_recall) / 2:.3f} "
        f"fake_recall={fake_recall:.3f} real_recall={real_recall:.3f} "
        f"cm=[tp={tp}, fn={fn}, fp={fp}, tn={tn}]"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        choices=("triclass", "community-forensics"),
        default="triclass",
    )
    args = parser.parse_args()
    fake_paths, real_paths = select_paths()
    with TemporaryDirectory(prefix="facetrust-external-") as temp_dir:
        directory = Path(temp_dir)
        if args.model == "community-forensics":
            fake_local = download_images(directory, fake_paths[20:])
            real_local = download_images(directory, real_paths[20:])
            test_paths = fake_local + real_local
            test_labels = np.asarray([1] * 20 + [0] * 20, dtype=np.int64)
            community_scores = predict_community_forensics(test_paths)
            triclass_scores = predict_triclass(test_paths)
            summarize("community-test", test_labels, community_scores, 0.5)
            summarize("triclass-test", test_labels, triclass_scores, 0.805)
            ensemble_scores = np.maximum(
                community_scores,
                (triclass_scores >= 0.805).astype(np.float64),
            )
            summarize("ensemble-test", test_labels, ensemble_scores, 0.5)
            return

        fake_local = download_images(directory, fake_paths)
        real_local = download_images(directory, real_paths)

        calibration_paths = fake_local[:20] + real_local[:20]
        calibration_labels = np.asarray([1] * 20 + [0] * 20, dtype=np.int64)
        test_paths = fake_local[20:] + real_local[20:]
        test_labels = np.asarray([1] * 20 + [0] * 20, dtype=np.int64)

        calibration_scores = predict_triclass(calibration_paths)
        threshold = select_threshold(calibration_labels, calibration_scores)
        summarize("calibration", calibration_labels, calibration_scores, threshold)

        test_scores = predict_triclass(test_paths)
        summarize("test-default", test_labels, test_scores, 0.5)
        summarize("test-calibrated", test_labels, test_scores, threshold)
        print(f"selected_threshold={threshold:.3f}")


if __name__ == "__main__":
    main()
