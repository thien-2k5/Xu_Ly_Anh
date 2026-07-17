from __future__ import annotations

import argparse
import json
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from facetrust_benchmark.web import app

PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE_DIR = PROJECT_DIR / "data" / "demo-images"
DEFAULT_REPORT_DIR = PROJECT_DIR / "reports"


@dataclass(frozen=True)
class EvaluationRow:
    file: str
    expected: str
    predicted: str
    correct: bool
    fake_risk_index: float
    decision_margin: float
    risk_band: str
    face_detected: bool
    scan_id: str
    latency_ms: float
    status_code: int
    error: str | None


def expected_label(path: Path) -> str:
    number = int(path.name.split("_", 1)[0])
    return "real" if number % 2 == 1 else "fake"


def iter_images(image_dir: Path) -> list[Path]:
    suffixes = {".jfif", ".jpg", ".jpeg", ".png", ".webp"}
    return sorted(
        path
        for path in image_dir.iterdir()
        if path.is_file() and path.suffix.lower() in suffixes and path.name[:3].isdigit()
    )


def post_image(client: TestClient, path: Path) -> EvaluationRow:
    expected = expected_label(path)
    started = time.perf_counter()
    with path.open("rb") as handle:
        response = client.post(
            "/api/detect",
            files={"image": (path.name, handle, f"image/{path.suffix.lstrip('.')}")},
        )
    latency_ms = (time.perf_counter() - started) * 1000

    if response.status_code != 200:
        return EvaluationRow(
            file=path.name,
            expected=expected,
            predicted="error",
            correct=False,
            fake_risk_index=0.0,
            decision_margin=0.0,
            risk_band="error",
            face_detected=False,
            scan_id="",
            latency_ms=latency_ms,
            status_code=response.status_code,
            error=response.text[:500],
        )

    payload = response.json()
    presentation = payload["presentation"]
    predicted = str(payload["label"])
    return EvaluationRow(
        file=path.name,
        expected=expected,
        predicted=predicted,
        correct=predicted == expected,
        fake_risk_index=float(presentation["fake_risk_index"]),
        decision_margin=float(presentation["decision_margin"]),
        risk_band=str(presentation["risk_band"]),
        face_detected=bool(payload["face_detected"]),
        scan_id=str(payload["scan_id"]),
        latency_ms=latency_ms,
        status_code=response.status_code,
        error=None,
    )


def metrics(rows: list[EvaluationRow]) -> dict[str, Any]:
    total = len(rows)
    correct = sum(row.correct for row in rows)
    tp = sum(row.expected == "fake" and row.predicted == "fake" for row in rows)
    tn = sum(row.expected == "real" and row.predicted == "real" for row in rows)
    fp = sum(row.expected == "real" and row.predicted == "fake" for row in rows)
    fn = sum(row.expected == "fake" and row.predicted != "fake" for row in rows)
    real_misses = sum(row.expected == "real" and row.predicted != "real" for row in rows)
    predicted_real = sum(row.predicted == "real" for row in rows)
    uncertain = sum(row.predicted == "uncertain" for row in rows)
    latencies = [row.latency_ms for row in rows]

    precision_fake = safe_div(tp, tp + fp)
    recall_fake = safe_div(tp, tp + fn)
    precision_real = safe_div(tn, predicted_real)
    recall_real = safe_div(tn, tn + real_misses)

    return {
        "total": total,
        "correct": correct,
        "accuracy": safe_div(correct, total),
        "fake_precision": precision_fake,
        "fake_recall": recall_fake,
        "fake_f1": f1(precision_fake, recall_fake),
        "real_precision": precision_real,
        "real_recall": recall_real,
        "real_f1": f1(precision_real, recall_real),
        "uncertain_rate": safe_div(uncertain, total),
        "confusion_matrix": {
            "true_fake_pred_fake": tp,
            "true_fake_pred_not_fake": fn,
            "true_real_pred_fake": fp,
            "true_real_pred_real": tn,
            "true_real_pred_not_real": real_misses,
            "uncertain": uncertain,
        },
        "face_detection_rate": safe_div(sum(row.face_detected for row in rows), total),
        "api_success_rate": safe_div(sum(row.status_code == 200 for row in rows), total),
        "latency_ms": {
            "mean": statistics.fmean(latencies) if latencies else 0.0,
            "median": statistics.median(latencies) if latencies else 0.0,
            "p95": percentile(latencies, 95),
            "max": max(latencies) if latencies else 0.0,
        },
    }


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


def write_reports(
    *,
    report_dir: Path,
    image_dir: Path,
    rows: list[EvaluationRow],
    summary: dict[str, Any],
) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "image_dir": str(image_dir.relative_to(PROJECT_DIR)),
        "summary": summary,
        "rows": [row.__dict__ for row in rows],
    }
    (report_dir / "evaluation_results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (report_dir / "evaluation_results.md").write_text(
        render_markdown(payload),
        encoding="utf-8",
    )


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = payload["rows"]
    cm = summary["confusion_matrix"]
    latency = summary["latency_ms"]
    lines = [
        "# FaceTrust Evaluation Results",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Image directory: `{payload['image_dir']}`",
        f"- Total images: `{summary['total']}`",
        "",
        "## Summary Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Accuracy | {pct(summary['accuracy'])} |",
        f"| Fake precision | {pct(summary['fake_precision'])} |",
        f"| Fake recall | {pct(summary['fake_recall'])} |",
        f"| Fake F1 | {pct(summary['fake_f1'])} |",
        f"| Real precision | {pct(summary['real_precision'])} |",
        f"| Real recall | {pct(summary['real_recall'])} |",
        f"| Real F1 | {pct(summary['real_f1'])} |",
        f"| Uncertain rate | {pct(summary['uncertain_rate'])} |",
        f"| Face detection rate | {pct(summary['face_detection_rate'])} |",
        f"| API success rate | {pct(summary['api_success_rate'])} |",
        "",
        "## Confusion Matrix",
        "",
        "| Ground truth | Correct class | Wrong/uncertain |",
        "| --- | ---: | ---: |",
        f"| Fake | {cm['true_fake_pred_fake']} | {cm['true_fake_pred_not_fake']} |",
        f"| Real | {cm['true_real_pred_real']} | {cm['true_real_pred_not_real']} |",
        "",
        "## Pipeline Timing",
        "",
        "| Timing | Milliseconds |",
        "| --- | ---: |",
        f"| Mean | {latency['mean']:.1f} |",
        f"| Median | {latency['median']:.1f} |",
        f"| P95 | {latency['p95']:.1f} |",
        f"| Max | {latency['max']:.1f} |",
        "",
        "## Per-image Results",
        "",
        "| File | Expected | Predicted | Correct | Risk | Margin | Face | Latency ms |",
        "| --- | --- | --- | --- | ---: | ---: | --- | ---: |",
    ]
    for row in rows:
        table_row = (
            "| {file} | {expected} | {predicted} | {correct} | {risk} | "
            "{confidence} | {face} | {latency:.1f} |"
        )
        lines.append(
            table_row.format(
                file=row["file"],
                expected=row["expected"],
                predicted=row["predicted"],
                correct="yes" if row["correct"] else "no",
                risk=pct(row["fake_risk_index"]),
                confidence=pct(row["decision_margin"]),
                face="yes" if row["face_detected"] else "no",
                latency=row["latency_ms"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "This report evaluates the current deployed upload pipeline on the curated "
                "public-figure stress set."
            ),
            (
                f"The pipeline API completed {pct(summary['api_success_rate'])} of requests "
                f"and detected faces in {pct(summary['face_detection_rate'])} of images."
            ),
            (
                f"Model-level accuracy on this set is {pct(summary['accuracy'])}; "
                f"fake recall is {pct(summary['fake_recall'])}."
            ),
            (
                "The decision margin is distance from the active threshold, not a calibrated "
                "probability that the verdict is correct."
            ),
            (
                "This is useful evidence for the report: the system is operational end-to-end, "
                "while the model needs further cross-domain fine-tuning before being claimed as "
                "production-grade."
            ),
            (
                "For a stronger thesis-grade result, add a larger held-out split containing "
                "face-swap, reenactment, diffusion-generated portraits, compressed social-media "
                "images, and real celebrity/public-figure photos."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the FaceTrust upload pipeline.")
    parser.add_argument("--image-dir", type=Path, default=DEFAULT_IMAGE_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    image_dir = args.image_dir.resolve()
    images = iter_images(image_dir)
    if not images:
        raise SystemExit(f"No numbered JPG images found in {image_dir}")

    client = TestClient(app)
    health = client.get("/api/health")
    health.raise_for_status()

    rows = [post_image(client, path) for path in images]
    summary = metrics(rows)
    if not args.no_write:
        write_reports(
            report_dir=args.report_dir.resolve(),
            image_dir=image_dir,
            rows=rows,
            summary=summary,
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
