from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from facetrust_benchmark import deepfake_detector
from facetrust_benchmark.web import app


def image_bytes(color: tuple[int, int, int]) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (128, 128), color=color).save(buffer, format="PNG")
    return buffer.getvalue()


def test_health_endpoint_reports_detector_task() -> None:
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["task"] == "image-deepfake-detection"
    assert payload["engine"] == "ai-vision-core"
    assert "gemini" not in payload


def test_detect_endpoint_accepts_image(monkeypatch, tmp_path: Path) -> None:
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
    client = TestClient(app)
    response = client.post(
        "/api/detect",
        files={"image": ("face.png", image_bytes((200, 160, 120)), "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["label"] in {"real", "fake", "uncertain"}
    assert 0 <= payload["presentation"]["fake_risk_index"] <= 1
    assert 0 <= payload["presentation"]["decision_margin"] <= 1
    assert "review" not in payload
    deepfake_detector._load_detector.cache_clear()


