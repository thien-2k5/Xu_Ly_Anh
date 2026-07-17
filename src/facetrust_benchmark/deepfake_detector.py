from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from facetrust_benchmark.image_io import load_rgb, validate_image
from facetrust_benchmark.settings import (
    COMMUNITY_FORENSICS_DIR,
    DETECTOR_MODEL_PATH,
    FACE_FORGERY_DETECTOR_DIR,
    TRICLASS_DETECTOR_DIR,
)


@dataclass(frozen=True)
class DetectionResult:
    filename: str
    label: str
    fake_probability: float
    confidence: float
    threshold: float
    backend: str
    face_detected: bool
    face_box: tuple[int, int, int, int] | None
    evidence: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_deepfake(image_path: str | Path) -> DetectionResult:
    detector = _load_detector()
    return detector.detect(Path(image_path))


def warm_detector() -> None:
    _load_detector()


@lru_cache(maxsize=1)
def _load_detector() -> DetectorBackend:
    load_notes: list[str] = []
    community_detector = None
    triclass_detector = None

    if FACE_FORGERY_DETECTOR_DIR.exists():
        try:
            primary = FaceForgeryDetector(FACE_FORGERY_DETECTOR_DIR)
            if DETECTOR_MODEL_PATH.exists():
                auxiliary = TorchCheckpointDetector(DETECTOR_MODEL_PATH)
                return AdaptiveFaceForgeryDetector(primary, auxiliary)
            return primary
        except Exception as exc:
            load_notes.append(f"Cannot load face-forgery detector: {exc}")

    if COMMUNITY_FORENSICS_DIR.exists():
        try:
            community_detector = CommunityForensicsDetector(COMMUNITY_FORENSICS_DIR)
        except Exception as exc:
            load_notes.append(f"Cannot load Community Forensics detector: {exc}")

    if TRICLASS_DETECTOR_DIR.exists():
        try:
            triclass_detector = TriClassImageDetector(TRICLASS_DETECTOR_DIR)
        except Exception as exc:
            load_notes.append(f"Cannot load tri-class detector: {exc}")

    if community_detector is not None:
        return community_detector
    if triclass_detector is not None:
        return triclass_detector

    if DETECTOR_MODEL_PATH.exists():
        try:
            return TorchCheckpointDetector(DETECTOR_MODEL_PATH)
        except Exception as exc:
            return ForensicBaselineDetector(
                notes=[f"Không tải được model đã train, dùng baseline: {exc}"]
            )
    return ForensicBaselineDetector(
        notes=[
            "Chưa có models/deepfake_detector.pt; kết quả hiện tại là forensic baseline.",
            "Train model bằng scripts/train_deepfake_detector.py để tăng độ chính xác.",
        ]
    )


class DetectorBackend:
    def detect(self, image_path: Path) -> DetectionResult:
        raise NotImplementedError


class FaceForgeryDetector(DetectorBackend):
    def __init__(self, model_dir: Path) -> None:
        import torch
        from deepguard import ms_eff_gcvit_b0
        from safetensors.torch import load_file
        from torchvision import transforms

        self.model = ms_eff_gcvit_b0(pretrained=False, dataset="ff++")
        state_dict = {
            key.removeprefix("model."): value
            for key, value in load_file(model_dir / "model.safetensors").items()
        }
        self.model.load_state_dict(state_dict)
        self.model.eval()
        self.threshold = 0.50
        self.real_threshold = 0.50
        self.backend = "ms-eff-gcvit-b0-ffpp"
        self.transform = transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.Resize((224, 224), antialias=True),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=(0.485, 0.456, 0.406),
                    std=(0.229, 0.224, 0.225),
                ),
            ]
        )
        self._torch = torch

    def detect(self, image_path: Path) -> DetectionResult:
        validate_image(image_path)
        image_rgb = load_rgb(image_path)
        face_box = _detect_primary_face(image_rgb)
        crop = _crop_face_or_center(image_rgb, face_box)
        # The released checkpoint was trained and published with face-crop input.
        # Feeding the full frame lets background and clothing dominate small faces.
        tensor = self.transform(crop).unsqueeze(0)
        with self._torch.inference_mode():
            probability = self.model(tensor).sigmoid().item()

        evidence = _forensic_features(crop)
        evidence.update(_quality_evidence(image_rgb, face_box))
        evidence["face_forgery_probability"] = probability
        evidence["face_forgery_fake_threshold"] = self.threshold
        evidence["face_forgery_real_threshold"] = self.real_threshold
        risk_index = _decision_risk_at_threshold(probability, self.threshold)
        if probability >= self.threshold:
            label = "fake"
        elif face_box is not None and probability <= self.real_threshold:
            label = "real"
        else:
            label = "uncertain"
        confidence = _decision_confidence(
            label=label,
            risk_index=risk_index,
            face_score=probability,
            fake_votes=int(label == "fake"),
            face_detected=face_box is not None,
        )
        return DetectionResult(
            filename=image_path.name,
            label=label,
            fake_probability=round(risk_index, 4),
            confidence=round(confidence, 4),
            threshold=self.threshold,
            backend=self.backend,
            face_detected=face_box is not None,
            face_box=face_box,
            evidence={key: round(float(value), 4) for key, value in evidence.items()},
            notes=[],
        )


class CommunityForensicsDetector(DetectorBackend):
    def __init__(self, model_dir: Path) -> None:
        import timm
        import torch
        from safetensors.torch import load_file
        from torchvision import transforms

        self.model = timm.create_model(
            "vit_small_patch16_384.augreg_in21k_ft_in1k",
            pretrained=False,
        )
        self.model.head = torch.nn.Linear(384, 1)
        state_dict = {
            key.removeprefix("vit."): value
            for key, value in load_file(model_dir / "model.safetensors").items()
        }
        self.model.load_state_dict(state_dict)
        self.model.eval()
        self.threshold = 0.5
        self.backend = "community-forensics-384"
        self.transform = transforms.Compose(
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

    def detect(self, image_path: Path) -> DetectionResult:
        import torch
        from PIL import Image

        validate_image(image_path)
        image_rgb = load_rgb(image_path)
        face_box = _detect_primary_face(image_rgb)
        crop = _crop_face_or_center(image_rgb, face_box)
        tensor = self.transform(Image.fromarray(image_rgb)).unsqueeze(0)
        with torch.inference_mode():
            probability = self.model(tensor).sigmoid().item()

        evidence = _forensic_features(crop)
        evidence["community_fake_probability"] = probability
        return _result(
            image_path=image_path,
            fake_probability=probability,
            threshold=self.threshold,
            backend=self.backend,
            face_box=face_box,
            evidence=evidence,
            notes=[],
        )


class TriClassImageDetector(DetectorBackend):
    def __init__(self, model_dir: Path) -> None:
        from transformers import AutoImageProcessor, AutoModelForImageClassification

        self.processor = AutoImageProcessor.from_pretrained(model_dir, local_files_only=True)
        self.model = AutoModelForImageClassification.from_pretrained(
            model_dir,
            local_files_only=True,
        )
        self.model.eval()
        labels = {
            int(index): str(label).lower()
            for index, label in self.model.config.id2label.items()
        }
        self.fake_indices = [
            index
            for index, label in labels.items()
            if label in {"artificial", "deepfake", "fake"}
        ]
        if not self.fake_indices:
            raise ValueError(f"Cannot infer fake classes from labels: {labels}")
        self.labels = labels
        self.threshold = 0.805
        self.backend = "triclass-ai-deepfake-real"

    def detect(self, image_path: Path) -> DetectionResult:
        import torch
        from PIL import Image

        validate_image(image_path)
        image_rgb = load_rgb(image_path)
        face_box = _detect_primary_face(image_rgb)
        crop = _crop_face_or_center(image_rgb, face_box)
        inputs = self.processor(images=Image.fromarray(image_rgb), return_tensors="pt")
        with torch.inference_mode():
            probabilities = self.model(**inputs).logits.softmax(dim=1)[0]
        probability = sum(probabilities[index].item() for index in self.fake_indices)
        evidence = _forensic_features(crop)
        for index, label in self.labels.items():
            evidence[f"triclass_{label}_probability"] = probabilities[index].item()
        evidence["triclass_fake_probability"] = probability
        return _result(
            image_path=image_path,
            fake_probability=probability,
            threshold=self.threshold,
            backend=self.backend,
            face_box=face_box,
            evidence=evidence,
            notes=[],
        )


class GeneralizationEnsembleDetector(DetectorBackend):
    def __init__(
        self,
        community: DetectorBackend,
        triclass: DetectorBackend,
        *,
        notes: list[str] | None = None,
    ) -> None:
        self.community = community
        self.triclass = triclass
        self.notes = notes or []
        self.threshold = 0.5
        self.backend = "community-forensics-384+triclass-calibrated"

    def detect(self, image_path: Path) -> DetectionResult:
        community_result = self.community.detect(image_path)
        triclass_result = self.triclass.detect(image_path)
        triclass_calibrated = _rescale_probability_at_threshold(
            triclass_result.fake_probability,
            triclass_result.threshold,
        )
        probability = max(community_result.fake_probability, triclass_calibrated)
        evidence = dict(community_result.evidence)
        evidence.update(
            {
                key: value
                for key, value in triclass_result.evidence.items()
                if key.startswith("triclass_")
            }
        )
        evidence["triclass_calibrated_probability"] = triclass_calibrated
        evidence["ensemble_agreement"] = float(
            community_result.label == triclass_result.label
        )
        return _result(
            image_path=image_path,
            fake_probability=probability,
            threshold=self.threshold,
            backend=self.backend,
            face_box=community_result.face_box,
            evidence=evidence,
            notes=[*community_result.notes, *triclass_result.notes, *self.notes],
        )


class FaceForgeryEnsembleDetector(DetectorBackend):
    def __init__(
        self,
        face_forgery: FaceForgeryDetector,
        community: DetectorBackend,
        triclass: DetectorBackend,
        *,
        notes: list[str] | None = None,
    ) -> None:
        self.face_forgery = face_forgery
        self.community = community
        self.triclass = triclass
        self.notes = notes or []
        self.threshold = 0.5
        self.backend = "ms-eff-gcvit-b0-ffpp+community+triclass"

    def detect(self, image_path: Path) -> DetectionResult:
        face_result = self.face_forgery.detect(image_path)
        community_result = self.community.detect(image_path)
        triclass_result = self.triclass.detect(image_path)

        face_score = face_result.fake_probability
        community_score = community_result.fake_probability
        triclass_score = triclass_result.fake_probability
        face_fake = face_score >= self.face_forgery.threshold
        community_fake = community_score >= community_result.threshold
        triclass_fake = triclass_score >= triclass_result.threshold
        fake_votes = sum((face_fake, community_fake, triclass_fake))

        face_risk = _decision_risk_at_threshold(
            face_score,
            self.face_forgery.threshold,
        )
        community_risk = _decision_risk_at_threshold(
            community_score,
            community_result.threshold,
        )
        triclass_risk = _decision_risk_at_threshold(
            triclass_score,
            triclass_result.threshold,
        )
        if not community_fake:
            community_risk *= 0.35
        if not triclass_fake:
            triclass_risk *= 0.35
        auxiliary_votes = sum((community_fake, triclass_fake))
        risk_index = face_risk
        if face_score <= self.face_forgery.real_threshold:
            risk_index = min(0.49, face_risk + auxiliary_votes * 0.03)
        elif not face_fake:
            risk_index = min(0.69, face_risk + auxiliary_votes * 0.05)
        else:
            risk_index = min(0.80, face_risk + auxiliary_votes * 0.02)

        if face_fake:
            label = "fake"
        elif face_result.face_detected and face_score <= self.face_forgery.real_threshold:
            label = "real"
        else:
            label = "uncertain"

        evidence = dict(face_result.evidence)
        evidence.update(
            {
                key: value
                for key, value in community_result.evidence.items()
                if key.startswith("community_")
            }
        )
        evidence.update(
            {
                key: value
                for key, value in triclass_result.evidence.items()
                if key.startswith("triclass_")
            }
        )
        evidence.update(
            {
                "face_forgery_decision_risk": face_risk,
                "community_decision_risk": community_risk,
                "triclass_calibrated_probability": triclass_risk,
                "fake_branch_votes": float(fake_votes),
                "ensemble_agreement": float(fake_votes in {0, 3}),
            }
        )
        confidence = _decision_confidence(
            label=label,
            risk_index=risk_index,
            face_score=face_score,
            fake_votes=fake_votes,
            face_detected=face_result.face_detected,
        )
        return DetectionResult(
            filename=image_path.name,
            label=label,
            fake_probability=round(float(risk_index), 4),
            confidence=round(confidence, 4),
            threshold=self.threshold,
            backend=self.backend,
            face_detected=face_result.face_detected,
            face_box=face_result.face_box,
            evidence={key: round(float(value), 4) for key, value in evidence.items()},
            notes=[
                *face_result.notes,
                *community_result.notes,
                *triclass_result.notes,
                *self.notes,
            ],
        )


class TorchCheckpointDetector(DetectorBackend):
    def __init__(self, model_path: Path) -> None:
        import torch

        checkpoint = torch.load(model_path, map_location="cpu")
        self.arch = checkpoint.get("arch", "efficientnet_b0")
        self.image_size = int(checkpoint.get("image_size", 224))
        self.threshold = float(checkpoint.get("threshold", 0.5))
        self.normalize = bool(checkpoint.get("normalize", True))
        self.crop_mode = checkpoint.get("crop_mode", "face")
        self.class_to_idx = checkpoint.get("class_to_idx", {"fake": 0, "real": 1})
        self.fake_index = int(self.class_to_idx.get("fake", 0))
        self.model = _build_model(self.arch, num_classes=len(self.class_to_idx))
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.eval()
        self.backend = f"torch-{self.arch}"

    def detect(self, image_path: Path) -> DetectionResult:
        import torch
        from torchvision import transforms

        validate_image(image_path)
        image_rgb = load_rgb(image_path)
        face_box = _detect_primary_face(image_rgb)
        crop = image_rgb if self.crop_mode == "full" else _crop_face_or_center(image_rgb, face_box)
        steps = [
            transforms.ToPILImage(),
            transforms.Resize((self.image_size, self.image_size), antialias=True),
            transforms.ToTensor(),
        ]
        if self.normalize:
            steps.append(
                transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
            )
        transform = transforms.Compose(steps)
        tensor = transform(crop).unsqueeze(0)
        with torch.no_grad():
            logits = self.model(tensor)
            probability = torch.softmax(logits, dim=1)[0, self.fake_index].item()
        evidence = _forensic_features(crop)
        return _result(
            image_path=image_path,
            fake_probability=probability,
            threshold=self.threshold,
            backend=self.backend,
            face_box=face_box,
            evidence=evidence,
            notes=[],
        )


class AdaptiveFaceForgeryDetector(DetectorBackend):
    small_face_ratio = 0.12
    small_face_threshold = 0.30

    def __init__(
        self,
        primary: FaceForgeryDetector,
        auxiliary: TorchCheckpointDetector,
    ) -> None:
        self.primary = primary
        self.auxiliary = auxiliary
        self.threshold = 0.5
        self.backend = f"{primary.backend}+adaptive-{auxiliary.backend}"

    def detect(self, image_path: Path) -> DetectionResult:
        primary_result = self.primary.detect(image_path)
        auxiliary_result = self.auxiliary.detect(image_path)
        evidence = dict(primary_result.evidence)
        primary_score = float(evidence["face_forgery_probability"])
        auxiliary_score = auxiliary_result.fake_probability
        face_ratio = float(evidence.get("face_area_ratio", 0.0))

        primary_fake = primary_result.face_detected and primary_score >= self.primary.threshold
        small_face_alert = (
            primary_result.face_detected
            and not primary_fake
            and face_ratio < self.small_face_ratio
            and auxiliary_score >= self.small_face_threshold
        )

        if primary_fake or small_face_alert:
            label = "fake"
        elif primary_result.face_detected:
            label = "real"
        else:
            label = "uncertain"

        primary_risk = _decision_risk_at_threshold(
            primary_score,
            self.primary.threshold,
        )
        auxiliary_risk = 0.0
        if small_face_alert:
            auxiliary_risk = 0.5 + 0.2 * _clamp01(
                (auxiliary_score - self.small_face_threshold)
                / (1.0 - self.small_face_threshold)
            )
        risk_index = max(primary_risk, auxiliary_risk)

        if primary_fake:
            decision_margin = _clamp01(
                (primary_score - self.primary.threshold)
                / (1.0 - self.primary.threshold)
            )
        elif small_face_alert:
            decision_margin = _clamp01(
                (auxiliary_score - self.small_face_threshold)
                / (1.0 - self.small_face_threshold)
            )
        elif label == "real":
            decision_margin = _clamp01(
                (self.primary.real_threshold - primary_score)
                / self.primary.real_threshold
            )
        else:
            decision_margin = 0.0

        evidence.update(
            {
                "auxiliary_face_probability": auxiliary_score,
                "small_face_ratio_threshold": self.small_face_ratio,
                "small_face_auxiliary_threshold": self.small_face_threshold,
                "primary_fake_flag": float(primary_fake),
                "small_face_alert_flag": float(small_face_alert),
                "decision_margin": decision_margin,
            }
        )
        return DetectionResult(
            filename=image_path.name,
            label=label,
            fake_probability=round(float(risk_index), 4),
            confidence=round(float(decision_margin), 4),
            threshold=self.threshold,
            backend=self.backend,
            face_detected=primary_result.face_detected,
            face_box=primary_result.face_box,
            evidence={key: round(float(value), 4) for key, value in evidence.items()},
            notes=[*primary_result.notes, *auxiliary_result.notes],
        )


class ForensicBaselineDetector(DetectorBackend):
    def __init__(self, notes: list[str] | None = None) -> None:
        self.notes = notes or []

    def detect(self, image_path: Path) -> DetectionResult:
        validate_image(image_path)
        image_rgb = load_rgb(image_path)
        face_box = _detect_primary_face(image_rgb)
        crop = _crop_face_or_center(image_rgb, face_box)
        evidence = _forensic_features(crop)
        probability = _baseline_probability(evidence, image_rgb.shape)
        return _result(
            image_path=image_path,
            fake_probability=probability,
            threshold=0.5,
            backend="forensic-baseline",
            face_box=face_box,
            evidence=evidence,
            notes=self.notes,
        )


def _rescale_probability_at_threshold(probability: float, threshold: float) -> float:
    probability = float(np.clip(probability, 0.0, 1.0))
    threshold = float(np.clip(threshold, 1e-6, 1.0 - 1e-6))
    if probability < threshold:
        return 0.5 * probability / threshold
    return 0.5 + 0.5 * (probability - threshold) / (1.0 - threshold)


def _decision_risk_at_threshold(probability: float, threshold: float) -> float:
    """Map a branch score to a bounded decision index, not a calibrated probability."""
    probability = float(np.clip(probability, 0.0, 1.0))
    threshold = float(np.clip(threshold, 1e-6, 1.0 - 1e-6))
    if probability < threshold:
        return 0.5 * probability / threshold
    return 0.5 + 0.3 * (probability - threshold) / (1.0 - threshold)


def _result(
    *,
    image_path: Path,
    fake_probability: float,
    threshold: float,
    backend: str,
    face_box: tuple[int, int, int, int] | None,
    evidence: dict[str, float],
    notes: list[str],
) -> DetectionResult:
    probability = float(np.clip(fake_probability, 0.0, 1.0))
    label = "fake" if probability >= threshold else "real"
    confidence = probability if label == "fake" else 1.0 - probability
    return DetectionResult(
        filename=image_path.name,
        label=label,
        fake_probability=round(probability, 4),
        confidence=round(float(confidence), 4),
        threshold=threshold,
        backend=backend,
        face_detected=face_box is not None,
        face_box=face_box,
        evidence={key: round(float(value), 4) for key, value in evidence.items()},
        notes=notes,
    )


def _build_model(arch: str, *, num_classes: int) -> Any:
    from torchvision import models

    if arch == "efficientnet_b0":
        model = models.efficientnet_b0(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier[1] = _linear(in_features, num_classes)
        return model
    if arch == "convnext_tiny":
        model = models.convnext_tiny(weights=None)
        in_features = model.classifier[2].in_features
        model.classifier[2] = _linear(in_features, num_classes)
        return model
    if arch == "mobilenet_v3_small":
        model = models.mobilenet_v3_small(weights=None)
        in_features = model.classifier[3].in_features
        model.classifier[3] = _linear(in_features, num_classes)
        return model
    raise ValueError(f"Unsupported detector architecture: {arch}")


def _linear(in_features: int, out_features: int) -> Any:
    import torch

    return torch.nn.Linear(in_features, out_features)


def _detect_primary_face(image_rgb: np.ndarray) -> tuple[int, int, int, int] | None:
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    x, y, width, height = max(faces, key=lambda item: item[2] * item[3])
    return _expand_box((int(x), int(y), int(width), int(height)), image_rgb.shape, scale=1.32)


def _expand_box(
    box: tuple[int, int, int, int],
    image_shape: tuple[int, ...],
    *,
    scale: float,
) -> tuple[int, int, int, int]:
    x, y, width, height = box
    center_x = x + width / 2
    center_y = y + height / 2
    size = max(width, height) * scale
    left = max(0, int(round(center_x - size / 2)))
    top = max(0, int(round(center_y - size / 2)))
    right = min(image_shape[1], int(round(center_x + size / 2)))
    bottom = min(image_shape[0], int(round(center_y + size / 2)))
    return (left, top, max(1, right - left), max(1, bottom - top))


def _crop_face_or_center(
    image_rgb: np.ndarray,
    face_box: tuple[int, int, int, int] | None,
    *,
    size: int = 256,
) -> np.ndarray:
    if face_box is None:
        height, width = image_rgb.shape[:2]
        side = min(height, width)
        x = (width - side) // 2
        y = (height - side) // 2
        crop = image_rgb[y : y + side, x : x + side]
    else:
        x, y, width, height = face_box
        crop = image_rgb[y : y + height, x : x + width]
    return cv2.resize(crop, (size, size), interpolation=cv2.INTER_AREA)


def _forensic_features(crop_rgb: np.ndarray) -> dict[str, float]:
    gray = cv2.cvtColor(crop_rgb, cv2.COLOR_RGB2GRAY)
    bgr = cv2.cvtColor(crop_rgb, cv2.COLOR_RGB2BGR)
    ok, encoded = cv2.imencode(".jpg", bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    if ok:
        decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        decoded_rgb = cv2.cvtColor(decoded, cv2.COLOR_BGR2RGB)
        diff = np.abs(crop_rgb.astype(np.float32) - decoded_rgb.astype(np.float32))
        ela_mean = float(diff.mean() / 255.0)
        ela_p95 = float(np.percentile(diff, 95) / 255.0)
    else:
        ela_mean = 0.0
        ela_p95 = 0.0

    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    blockiness = _blockiness(gray)
    high_frequency_ratio = _high_frequency_ratio(gray)
    blur = cv2.GaussianBlur(crop_rgb, (0, 0), 1.1)
    noise_residual = float(
        np.abs(crop_rgb.astype(np.float32) - blur.astype(np.float32)).mean() / 255.0
    )
    channel_gap = float(np.std(crop_rgb.reshape(-1, 3).mean(axis=0)) / 255.0)
    return {
        "ela_mean": ela_mean,
        "ela_p95": ela_p95,
        "laplacian_var": laplacian_var,
        "blockiness": blockiness,
        "high_frequency_ratio": high_frequency_ratio,
        "noise_residual": noise_residual,
        "channel_gap": channel_gap,
    }


def _quality_evidence(
    image_rgb: np.ndarray,
    face_box: tuple[int, int, int, int] | None,
) -> dict[str, float]:
    height, width = image_rgb.shape[:2]
    face_area_ratio = 0.0
    if face_box is not None:
        _, _, face_width, face_height = face_box
        face_area_ratio = (face_width * face_height) / (width * height)
    return {
        "image_width": float(width),
        "image_height": float(height),
        "short_side": float(min(width, height)),
        "face_area_ratio": float(face_area_ratio),
    }


def _decision_confidence(
    *,
    label: str,
    risk_index: float,
    face_score: float,
    fake_votes: int,
    face_detected: bool,
) -> float:
    if label == "fake":
        margin = _clamp01((face_score - 0.99) / 0.01)
        value = 0.61 + margin * 0.08 + max(0, fake_votes - 1) * 0.035
    elif label == "real":
        margin = _clamp01((0.5 - face_score) / 0.5)
        value = 0.68 + margin * 0.08
    else:
        distance = abs(risk_index - 0.5) * 2.0
        value = 0.51 + min(distance, 1.0) * 0.07
    if not face_detected:
        value -= 0.05
    return float(np.clip(value, 0.50, 0.79))


def _blockiness(gray: np.ndarray) -> float:
    values = gray.astype(np.float32)
    vertical = (
        np.abs(values[:, 8::8] - values[:, 7:-1:8]).mean() if values.shape[1] > 8 else 0.0
    )
    horizontal = (
        np.abs(values[8::8, :] - values[7:-1:8, :]).mean() if values.shape[0] > 8 else 0.0
    )
    return float(((vertical + horizontal) / 2.0) / 255.0)


def _high_frequency_ratio(gray: np.ndarray) -> float:
    values = gray.astype(np.float32)
    spectrum = np.fft.fftshift(np.fft.fft2(values))
    magnitude = np.abs(spectrum)
    height, width = values.shape
    yy, xx = np.ogrid[:height, :width]
    radius = np.sqrt((yy - height / 2) ** 2 + (xx - width / 2) ** 2)
    high = magnitude[radius > min(height, width) * 0.25].mean()
    low = magnitude[radius <= min(height, width) * 0.25].mean()
    return float(high / (low + 1e-6))


def _baseline_probability(evidence: dict[str, float], image_shape: tuple[int, ...]) -> float:
    laplacian = evidence["laplacian_var"]
    high_frequency = evidence["high_frequency_ratio"]
    noise = evidence["noise_residual"]
    ela_p95 = evidence["ela_p95"]
    blockiness = evidence["blockiness"]
    channel_gap = evidence["channel_gap"]
    height, width = image_shape[:2]
    short_side = min(height, width)

    smooth_face = _clamp01((170.0 - laplacian) / 170.0)
    low_detail = _clamp01((0.095 - high_frequency) / 0.095)
    low_noise = _clamp01((0.014 - noise) / 0.014)
    compressed_uniform = _clamp01((0.023 - ela_p95) / 0.023)
    block_score = _clamp01((blockiness - 0.010) / 0.020)
    low_resolution = _clamp01((320.0 - short_side) / 220.0)

    logit = (
        -1.15
        + smooth_face * 1.45
        + low_detail * 1.1
        + low_noise * 0.9
        + compressed_uniform * 0.7
        + block_score * 0.45
        + channel_gap * 0.55
        + low_resolution * 0.35
    )
    return 1.0 / (1.0 + math.exp(-logit))


def _clamp01(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))
