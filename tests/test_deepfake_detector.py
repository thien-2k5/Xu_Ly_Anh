from pathlib import Path

from PIL import Image

from facetrust_benchmark import deepfake_detector


def write_image(path: Path, color: tuple[int, int, int]) -> None:
    Image.new("RGB", (128, 128), color=color).save(path)


def test_forensic_baseline_returns_probability(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(deepfake_detector, "DETECTOR_MODEL_PATH", tmp_path / "missing.pt")
    monkeypatch.setattr(
        deepfake_detector,
        "COMMUNITY_FORENSICS_DIR",
        tmp_path / "missing-community",
    )
    monkeypatch.setattr(
        deepfake_detector,
        "TRICLASS_DETECTOR_DIR",
        tmp_path / "missing-triclass",
    )
    monkeypatch.setattr(
        deepfake_detector,
        "FACE_FORGERY_DETECTOR_DIR",
        tmp_path / "missing-face-forgery",
    )
    deepfake_detector._load_detector.cache_clear()
    image_path = tmp_path / "sample.png"
    write_image(image_path, (210, 180, 150))

    result = deepfake_detector.detect_deepfake(image_path)

    assert result.label in {"real", "fake"}
    assert 0 <= result.fake_probability <= 1
    assert result.backend == "forensic-baseline"
    assert "laplacian_var" in result.evidence
    deepfake_detector._load_detector.cache_clear()


class StubDetector(deepfake_detector.DetectorBackend):
    def __init__(
        self,
        probability: float,
        threshold: float,
        *,
        face_detected: bool = False,
    ) -> None:
        self.probability = probability
        self.threshold = threshold
        self.face_detected = face_detected
        self.backend = "stub"

    def detect(self, image_path: Path) -> deepfake_detector.DetectionResult:
        return deepfake_detector._result(
            image_path=image_path,
            fake_probability=self.probability,
            threshold=self.threshold,
            backend="stub",
            face_box=(0, 0, 64, 64) if self.face_detected else None,
            evidence={},
            notes=[],
        )


def test_generalization_ensemble_uses_calibrated_triclass_vote(tmp_path: Path) -> None:
    detector = deepfake_detector.GeneralizationEnsembleDetector(
        StubDetector(0.1, 0.5),
        StubDetector(0.81, 0.805),
    )

    result = detector.detect(tmp_path / "sample.jpg")

    assert result.label == "fake"
    assert result.backend == "community-forensics-384+triclass-calibrated"
    assert result.evidence["triclass_calibrated_probability"] > 0.5


def test_face_forgery_ensemble_can_return_uncertain(tmp_path: Path) -> None:
    face = StubDetector(0.8, 0.99)
    face.real_threshold = 0.5
    detector = deepfake_detector.FaceForgeryEnsembleDetector(
        face,
        StubDetector(0.1, 0.5),
        StubDetector(0.2, 0.805),
    )

    result = detector.detect(tmp_path / "sample.jpg")

    assert result.label == "uncertain"
    assert result.confidence <= 0.79


def test_auxiliary_branches_cannot_override_primary_real_zone(tmp_path: Path) -> None:
    face = StubDetector(0.1, 0.99, face_detected=True)
    face.real_threshold = 0.5
    detector = deepfake_detector.FaceForgeryEnsembleDetector(
        face,
        StubDetector(0.9, 0.5),
        StubDetector(0.9, 0.805),
    )

    result = detector.detect(tmp_path / "sample.jpg")

    assert result.label == "real"
    assert result.fake_probability < 0.5
    assert result.evidence["fake_branch_votes"] == 2


class AdaptivePrimaryStub:
    threshold = 0.5
    real_threshold = 0.5
    backend = "primary-stub"

    def __init__(self, score: float, face_ratio: float) -> None:
        self.score = score
        self.face_ratio = face_ratio

    def detect(self, image_path: Path) -> deepfake_detector.DetectionResult:
        return deepfake_detector.DetectionResult(
            filename=image_path.name,
            label="real",
            fake_probability=0.2,
            confidence=0.5,
            threshold=self.threshold,
            backend=self.backend,
            face_detected=True,
            face_box=(10, 10, 40, 40),
            evidence={
                "face_forgery_probability": self.score,
                "face_forgery_fake_threshold": self.threshold,
                "face_forgery_real_threshold": self.real_threshold,
                "face_area_ratio": self.face_ratio,
            },
        )


def test_adaptive_detector_uses_auxiliary_only_for_small_face(tmp_path: Path) -> None:
    auxiliary = StubDetector(0.415, 0.055, face_detected=True)
    small_face = deepfake_detector.AdaptiveFaceForgeryDetector(
        AdaptivePrimaryStub(0.425, 0.059),
        auxiliary,
    )
    large_face = deepfake_detector.AdaptiveFaceForgeryDetector(
        AdaptivePrimaryStub(0.425, 0.20),
        auxiliary,
    )

    small_result = small_face.detect(tmp_path / "small.jpg")
    large_result = large_face.detect(tmp_path / "large.jpg")

    assert small_result.label == "fake"
    assert small_result.evidence["small_face_alert_flag"] == 1
    assert 0 < small_result.evidence["decision_margin"] < 0.5
    assert large_result.label == "real"
