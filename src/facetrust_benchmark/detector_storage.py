from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from fastapi import UploadFile

from facetrust_benchmark.deepfake_detector import detect_deepfake
from facetrust_benchmark.image_io import validate_image
from facetrust_benchmark.settings import ALLOWED_IMAGE_SUFFIXES, MAX_UPLOAD_BYTES


def safe_suffix(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    return suffix if suffix in ALLOWED_IMAGE_SUFFIXES else ".png"


async def detect_upload(upload: UploadFile) -> dict[str, Any]:
    if upload is None or not upload.filename:
        raise ValueError("Image is required.")
    content = await upload.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("Image exceeds 16 MB.")
    suffix = safe_suffix(upload.filename)
    with TemporaryDirectory(prefix="facetrust-") as directory:
        path = Path(directory) / f"input{suffix}"
        path.write_bytes(content)
        validate_image(path)
        raw_result = (await asyncio.to_thread(detect_deepfake, path)).as_dict()

    return _public_result(
        raw_result,
        scan_id=_scan_id(content),
    )


def _public_result(
    raw_result: dict[str, Any],
    *,
    scan_id: str,
) -> dict[str, Any]:
    label = str(raw_result.get("label") or "uncertain")
    if label not in {"fake", "real", "uncertain"}:
        label = "uncertain"
    fake_probability = _clamp(float(raw_result.get("fake_probability") or 0.0), 0.0, 1.0)
    fake_risk_index = fake_probability
    evidence = raw_result.get("evidence") or {}
    decision_margin = _clamp(float(evidence.get("decision_margin") or 0.0), 0.0, 1.0)
    risk_band = _risk_band(fake_risk_index, label)
    signals = _signals(raw_result)

    return {
        "scan_id": scan_id,
        "label": label,
        "face_detected": bool(raw_result.get("face_detected")),
        "presentation": {
            "verdict": label,
            "verdict_label": _verdict_label(label),
            "title": _verdict_title(label),
            "kicker": _verdict_kicker(label),
            "summary": _verdict_summary(label, raw_result),
            "fake_risk_index": round(fake_risk_index, 3),
            "decision_margin": round(decision_margin, 3),
            "risk_band": risk_band,
            "engine_label": "FaceTrust Forensics",
            "review_label": "Phân tích đa mô hình",
            "signals": signals[:5],
        },
    }


def _risk_band(fake_risk_index: float, label: str) -> str:
    if label == "fake":
        return "Cao" if fake_risk_index >= 0.72 else "Cần kiểm tra"
    if label == "real":
        return "Thấp" if fake_risk_index <= 0.28 else "Thấp vừa"
    return "Chưa xác định"


def _verdict_label(label: str) -> str:
    return {
        "fake": "Nghi vấn fake",
        "real": "Khả năng real",
        "uncertain": "Chưa đủ bằng chứng",
    }[label]


def _verdict_title(label: str) -> str:
    return {
        "fake": "Kết luận: nghi vấn giả mạo",
        "real": "Kết luận: khả năng ảnh thật",
        "uncertain": "Kết luận: chưa đủ bằng chứng",
    }[label]


def _verdict_kicker(label: str) -> str:
    return {
        "fake": "Phát hiện tín hiệu vượt ngưỡng",
        "real": "Tín hiệu nằm trong vùng an toàn",
        "uncertain": "Các nhánh chưa tạo đủ đồng thuận",
    }[label]


def _verdict_summary(label: str, raw_result: dict[str, Any]) -> str:
    evidence = raw_result.get("evidence") or {}
    if label == "fake":
        if _number(evidence.get("small_face_alert_flag"), 0.0):
            return "Crop khuôn mặt nhỏ vượt ngưỡng cảnh báo của detector phụ."
        return "Detector chính trên vùng khuôn mặt vượt ngưỡng cảnh báo face-swap."
    if label == "real":
        return "Detector chính nằm dưới ngưỡng fake và không có cảnh báo khuôn mặt nhỏ."
    return "Không định vị được khuôn mặt đủ rõ để đưa ra kết luận."


def _signals(raw_result: dict[str, Any]) -> list[dict[str, str]]:
    evidence = raw_result.get("evidence") or {}
    signals: list[dict[str, str]] = []
    face_score = _number(evidence.get("face_forgery_probability"))
    fake_threshold = _number(evidence.get("face_forgery_fake_threshold"), 0.5)
    if face_score is not None:
        if face_score >= fake_threshold:
            region = "phía fake"
            kind = "risk"
        else:
            region = "phía real"
            kind = "quality"
        signals.append(
            {
                "kind": kind,
                "title": "Detector chính trên vùng khuôn mặt",
                "detail": (
                    f"Raw score {face_score:.3f}; ngưỡng quyết định là "
                    f"{fake_threshold:.3f}. Điểm hiện nằm về {region}; đây là score "
                    "của model, không phải xác suất đã được hiệu chuẩn."
                ),
            }
        )

    auxiliary_score = _number(evidence.get("auxiliary_face_probability"))
    small_face_threshold = _number(evidence.get("small_face_auxiliary_threshold"), 0.3)
    small_face_alert = bool(_number(evidence.get("small_face_alert_flag"), 0.0))
    face_ratio = _number(evidence.get("face_area_ratio"), 0.0)
    ratio_threshold = _number(evidence.get("small_face_ratio_threshold"), 0.12)
    small_face = face_ratio < ratio_threshold
    if auxiliary_score is not None:
        if small_face_alert:
            title = "Detector phụ kích hoạt chế độ khuôn mặt nhỏ"
            kind = "risk"
        elif auxiliary_score < small_face_threshold:
            title = "Detector phụ dưới ngưỡng bổ trợ"
            kind = "quality"
        else:
            title = "Detector phụ ghi nhận tín hiệu tham khảo"
            kind = "neutral"
        activation = "được áp dụng" if small_face else "không áp dụng với khuôn mặt đủ lớn"
        signals.append(
            {
                "kind": kind,
                "title": title,
                "detail": (
                    f"Raw score {auxiliary_score:.3f}; ngưỡng bổ trợ "
                    f"{small_face_threshold:.3f} chỉ {activation}. Detector này không "
                    "tự quyết định trên ảnh có khuôn mặt đủ lớn."
                ),
            }
        )

    if face_score is not None and auxiliary_score is not None:
        gap = abs(face_score - auxiliary_score)
        primary_region = "nghiêng fake" if face_score >= fake_threshold else "nghiêng real"
        auxiliary_region = (
            "có tín hiệu fake"
            if auxiliary_score >= small_face_threshold
            else "không vượt ngưỡng bổ trợ"
        )
        same_region = (face_score >= fake_threshold) == (
            auxiliary_score >= small_face_threshold
        )
        signals.append(
            {
                "kind": "quality" if same_region else "neutral",
                "title": "Đối chiếu hai góc nhìn",
                "detail": (
                    f"Nhánh chính {primary_region}; nhánh phụ {auxiliary_region}; "
                    f"độ lệch raw score {gap:.3f}. "
                    + (
                        "Hai detector đồng thuận."
                        if same_region
                        else "Hai detector chưa đồng thuận."
                    )
                ),
            }
        )

    width = _number(evidence.get("image_width"))
    height = _number(evidence.get("image_height"))
    face_box = raw_result.get("face_box")
    if not raw_result.get("face_detected"):
        signals.append(
            {
                "kind": "neutral",
                "title": "Không định vị được khuôn mặt",
                "detail": "Không có vùng mặt đủ rõ để chạy đối chiếu crop; kết luận bị giới hạn.",
            }
        )
    elif width is not None and height is not None and face_ratio is not None:
        box_text = ""
        if isinstance(face_box, (list, tuple)) and len(face_box) == 4:
            box_text = f"; crop {int(face_box[2])}×{int(face_box[3])} px"
        signals.append(
            {
                "kind": "neutral" if small_face else "quality",
                "title": "Kích thước vùng khuôn mặt",
                "detail": (
                    f"Ảnh {int(width)}×{int(height)} px{box_text}; khuôn mặt chiếm "
                    f"{face_ratio * 100:.1f}% khung hình. "
                    f"Ngưỡng khuôn mặt nhỏ là {ratio_threshold * 100:.0f}%."
                ),
            }
        )

    laplacian = _number(evidence.get("laplacian_var"))
    blockiness = _number(evidence.get("blockiness"))
    ela_p95 = _number(evidence.get("ela_p95"))
    noise = _number(evidence.get("noise_residual"))
    if None not in {laplacian, blockiness, ela_p95, noise}:
        sharpness = "thấp" if laplacian < 45 else "trung bình" if laplacian < 120 else "cao"
        compression = "cao" if blockiness > 0.045 else "vừa" if blockiness > 0.025 else "thấp"
        signals.append(
            {
                "kind": "neutral" if sharpness == "thấp" or compression == "cao" else "quality",
                "title": "Dấu vết chất lượng vùng mặt",
                "detail": (
                    f"Độ nét {sharpness} (Laplacian {laplacian:.1f}); nén khối {compression} "
                    f"({blockiness:.3f}); ELA p95 {ela_p95:.3f}; nhiễu dư {noise:.3f}. "
                    "Các số này mô tả chất lượng, không tự chứng minh ảnh fake."
                ),
            }
        )

    return signals


def _number(value: Any, default: float | None = None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _scan_id(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()[:10].upper()


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
