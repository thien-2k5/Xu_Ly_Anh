from __future__ import annotations

import argparse
import json
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from facetrust_benchmark.deepfake_detector import detect_deepfake, warm_detector

PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = PROJECT_DIR / "reports"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".jfif", ".png", ".webp"}

DEMO_SOURCE_FILES = {
    "01_04__talking_angry_couch__0XUW13RW_face0105.jpg",
    "01_11__walking_outside_cafe_disgusted__FAFWDR4W_face0036.jpg",
    "01_11__hugging_happy__4OJNJLOO_face0046.jpg",
    "01_11__meeting_serious__9OM3VE0Y_face0115.jpg",
    "01_12__outside_talking_still_laughing__TNI7KUZ6_face0003.jpg",
    "01_15__kitchen_still__02HILKYO_face0074.jpg",
    "01_11__talking_against_wall__9229VVZ3_face0076.jpg",
    "01_11__talking_against_wall__UQ0BOBNO_face0029.jpg",
}


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    fake_dir: Path
    real_dir: Path
    excluded_fake_names: frozenset[str] = frozenset()


@dataclass(frozen=True)
class EvaluationRow:
    dataset: str
    file: str
    expected: str
    predicted: str
    backend: str
    correct: bool
    face_detected: bool
    fake_risk_index: float
    decision_margin: float
    latency_ms: float


DATASETS = (
    DatasetSpec(
        name="DeepFake Facial",
        fake_dir=PROJECT_DIR / "data/benchmarks/deepfake-facial/Deep_Fakes/Fake",
        real_dir=PROJECT_DIR / "data/benchmarks/deepfake-facial/Deep_Fakes/Real",
        excluded_fake_names=frozenset(DEMO_SOURCE_FILES),
    ),
    DatasetSpec(
        name="Celeb-DF-v2 sample",
        fake_dir=PROJECT_DIR / "data/benchmarks/celebdf-v2-sample",
        real_dir=PROJECT_DIR / "data/benchmarks/celebdf-v2-real-sample",
    ),
)


def iter_images(directory: Path, excluded_names: frozenset[str]) -> list[Path]:
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file()
        and path.suffix.lower() in IMAGE_SUFFIXES
        and path.name not in excluded_names
    )


def select_images(paths: list[Path], limit_per_class: int | None) -> list[Path]:
    if limit_per_class is None or limit_per_class >= len(paths):
        return paths
    if limit_per_class <= 0:
        return []
    if limit_per_class == 1:
        return [paths[0]]

    # Deterministic coverage across the sorted source list instead of taking one
    # dense block of consecutive frames from the same video.
    indices = {
        round(index * (len(paths) - 1) / (limit_per_class - 1))
        for index in range(limit_per_class)
    }
    return [paths[index] for index in sorted(indices)]


def evaluate_image(dataset: str, expected: str, path: Path) -> EvaluationRow:
    started = time.perf_counter()
    result = detect_deepfake(path)
    latency_ms = (time.perf_counter() - started) * 1000
    margin = float(result.evidence.get("decision_margin", result.confidence))
    return EvaluationRow(
        dataset=dataset,
        file=path.name,
        expected=expected,
        predicted=result.label,
        backend=result.backend,
        correct=result.label == expected,
        face_detected=result.face_detected,
        fake_risk_index=float(result.fake_probability),
        decision_margin=margin,
        latency_ms=latency_ms,
    )


def safe_div(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def f1(precision: float, recall: float) -> float:
    return safe_div(2 * precision * recall, precision + recall)


def percentile(values: list[float], percent: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((percent / 100) * (len(ordered) - 1)))
    return ordered[index]


def metrics(rows: list[EvaluationRow]) -> dict[str, Any]:
    total = len(rows)
    tp = sum(row.expected == "fake" and row.predicted == "fake" for row in rows)
    fn_real = sum(row.expected == "fake" and row.predicted == "real" for row in rows)
    fn_uncertain = sum(
        row.expected == "fake" and row.predicted == "uncertain" for row in rows
    )
    tn = sum(row.expected == "real" and row.predicted == "real" for row in rows)
    fp_fake = sum(row.expected == "real" and row.predicted == "fake" for row in rows)
    fp_uncertain = sum(
        row.expected == "real" and row.predicted == "uncertain" for row in rows
    )
    predicted_fake = sum(row.predicted == "fake" for row in rows)
    predicted_real = sum(row.predicted == "real" for row in rows)
    expected_fake = sum(row.expected == "fake" for row in rows)
    expected_real = sum(row.expected == "real" for row in rows)
    uncertain = sum(row.predicted == "uncertain" for row in rows)
    correct = tp + tn
    fake_precision = safe_div(tp, predicted_fake)
    fake_recall = safe_div(tp, expected_fake)
    real_precision = safe_div(tn, predicted_real)
    real_recall = safe_div(tn, expected_real)
    latencies = [row.latency_ms for row in rows]

    return {
        "total": total,
        "expected_fake": expected_fake,
        "expected_real": expected_real,
        "correct": correct,
        "strict_accuracy": safe_div(correct, total),
        "balanced_accuracy": (fake_recall + real_recall) / 2,
        "fake_precision": fake_precision,
        "fake_recall": fake_recall,
        "fake_f1": f1(fake_precision, fake_recall),
        "real_precision": real_precision,
        "real_recall": real_recall,
        "real_f1": f1(real_precision, real_recall),
        "uncertain_rate": safe_div(uncertain, total),
        "face_detection_rate": safe_div(sum(row.face_detected for row in rows), total),
        "confusion_matrix": {
            "true_fake_pred_fake": tp,
            "true_fake_pred_real": fn_real,
            "true_fake_pred_uncertain": fn_uncertain,
            "true_real_pred_fake": fp_fake,
            "true_real_pred_real": tn,
            "true_real_pred_uncertain": fp_uncertain,
        },
        "latency_ms": {
            "mean": statistics.fmean(latencies) if latencies else 0.0,
            "median": statistics.median(latencies) if latencies else 0.0,
            "p95": percentile(latencies, 95),
            "max": max(latencies) if latencies else 0.0,
        },
    }


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# FaceTrust Cross-dataset Evaluation",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Detector backend: `{payload['detector_backend']}`",
        f"- Protocol: `{payload['protocol']}`",
        "- Demo-source frames are excluded from DeepFake Facial.",
        "- An `uncertain` output is counted as incorrect in strict accuracy.",
        "- Frame-level samples may be correlated when extracted from the same video.",
        "",
        "## Results by dataset",
        "",
        (
            "| Dataset | N | Strict accuracy | Balanced accuracy | Fake recall | "
            "Real recall | Uncertain |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in payload["datasets"]:
        summary = result["summary"]
        lines.append(
            f"| {result['name']} | {summary['total']} | "
            f"{pct(summary['strict_accuracy'])} | {pct(summary['balanced_accuracy'])} | "
            f"{pct(summary['fake_recall'])} | {pct(summary['real_recall'])} | "
            f"{pct(summary['uncertain_rate'])} |"
        )
    overall = payload["overall"]
    lines.append(
        f"| **Combined** | **{overall['total']}** | "
        f"**{pct(overall['strict_accuracy'])}** | "
        f"**{pct(overall['balanced_accuracy'])}** | "
        f"**{pct(overall['fake_recall'])}** | **{pct(overall['real_recall'])}** | "
        f"**{pct(overall['uncertain_rate'])}** |"
    )
    lines.extend(
        [
            "",
            "## Combined confusion matrix",
            "",
            "| Ground truth | Predicted fake | Predicted real | Uncertain |",
            "| --- | ---: | ---: | ---: |",
            (
                "| Fake | {true_fake_pred_fake} | {true_fake_pred_real} | "
                "{true_fake_pred_uncertain} |"
            ).format(**overall["confusion_matrix"]),
            (
                "| Real | {true_real_pred_fake} | {true_real_pred_real} | "
                "{true_real_pred_uncertain} |"
            ).format(**overall["confusion_matrix"]),
            "",
            "## Interpretation",
            "",
            (
                "Strict accuracy is the fraction of all frames whose final label exactly "
                "matches ground truth. Balanced accuracy is the mean of fake recall and "
                "real recall, so the two classes contribute equally."
            ),
            (
                "The fake risk index and decision margin are internal decision scores, not "
                "calibrated probabilities that a verdict is correct."
            ),
            (
                "These results measure cross-domain generalization of the deployed checkpoint. "
                "They do not inherit the much higher same-dataset accuracy published by the "
                "model author."
            ),
            "",
            "## Per-dataset confusion matrices",
            "",
        ]
    )
    for result in payload["datasets"]:
        cm = result["summary"]["confusion_matrix"]
        lines.extend(
            [
                f"### {result['name']}",
                "",
                "| Ground truth | Predicted fake | Predicted real | Uncertain |",
                "| --- | ---: | ---: | ---: |",
                (
                    "| Fake | {true_fake_pred_fake} | {true_fake_pred_real} | "
                    "{true_fake_pred_uncertain} |"
                ).format(**cm),
                (
                    "| Real | {true_real_pred_fake} | {true_real_pred_real} | "
                    "{true_real_pred_uncertain} |"
                ).format(**cm),
                "",
            ]
        )
    return "\n".join(lines)


def write_reports(payload: dict[str, Any], report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "cross_dataset_results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (report_dir / "cross_dataset_results.md").write_text(
        render_markdown(payload),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate FaceTrust on independent local benchmark datasets."
    )
    parser.add_argument(
        "--limit-per-class",
        type=int,
        default=None,
        help="Optional deterministic sample count for each class and dataset.",
    )
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    warm_detector()
    dataset_payloads: list[dict[str, Any]] = []
    all_rows: list[EvaluationRow] = []

    for spec in DATASETS:
        fake_paths = select_images(
            iter_images(spec.fake_dir, spec.excluded_fake_names),
            args.limit_per_class,
        )
        real_paths = select_images(
            iter_images(spec.real_dir, frozenset()),
            args.limit_per_class,
        )
        rows = [
            *(evaluate_image(spec.name, "fake", path) for path in fake_paths),
            *(evaluate_image(spec.name, "real", path) for path in real_paths),
        ]
        all_rows.extend(rows)
        dataset_payloads.append(
            {
                "name": spec.name,
                "fake_dir": str(spec.fake_dir.relative_to(PROJECT_DIR)),
                "real_dir": str(spec.real_dir.relative_to(PROJECT_DIR)),
                "excluded_fake_files": sorted(spec.excluded_fake_names),
                "summary": metrics(rows),
                "rows": [asdict(row) for row in rows],
            }
        )

    payload = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "detector_backend": all_rows[0].backend if all_rows else "unknown",
        "protocol": (
            "all available frames per class"
            if args.limit_per_class is None
            else f"deterministic coverage, up to {args.limit_per_class} frames per class"
        ),
        "datasets": dataset_payloads,
        "overall": metrics(all_rows),
    }
    if not args.no_write:
        write_reports(payload, args.report_dir.resolve())
    console_payload = {
        "datasets": [
            {"name": result["name"], "summary": result["summary"]}
            for result in dataset_payloads
        ],
        "overall": payload["overall"],
    }
    print(json.dumps(console_payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
