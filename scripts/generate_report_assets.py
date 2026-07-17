# ruff: noqa: E501
from __future__ import annotations

import json
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

PROJECT_DIR = Path(__file__).resolve().parents[1]
ASSET_DIR = PROJECT_DIR / "docs" / "report-assets"
REPORT_JSON = PROJECT_DIR / "reports" / "cross_dataset_results.json"

FONT_REGULAR = Path("C:/Windows/Fonts/arial.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/arialbd.ttf")
FONT_ITALIC = Path("C:/Windows/Fonts/ariali.ttf")

INK = "#102136"
MUTED = "#5E6C7E"
BLUE = "#176B87"
TEAL = "#0D8A8F"
GREEN = "#15805D"
RED = "#C53A32"
GOLD = "#B57918"
PALE_BLUE = "#E8F2F6"
PALE_TEAL = "#E7F5F3"
PALE_RED = "#FBECE9"
PALE_GOLD = "#FFF4DD"
LINE = "#C9D5E1"
PAPER = "#FFFFFF"
CANVAS = "#F6F8FB"


def font(size: int, *, bold: bool = False, italic: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT_ITALIC if italic else FONT_REGULAR
    return ImageFont.truetype(str(path), size=size)


def rounded_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    fill: str = PAPER,
    outline: str = LINE,
    radius: int = 18,
    width: int = 3,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def center_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    *,
    fill: str = INK,
    spacing: int = 8,
) -> None:
    left, top, right, bottom = box
    max_width = right - left - 36
    average_char = max(text_font.getlength("M"), 1)
    chars = max(8, int(max_width / average_char * 1.6))
    wrapped = "\n".join(textwrap.wrap(text, width=chars, break_long_words=False))
    bounds = draw.multiline_textbbox((0, 0), wrapped, font=text_font, spacing=spacing, align="center")
    text_width = bounds[2] - bounds[0]
    text_height = bounds[3] - bounds[1]
    draw.multiline_text(
        ((left + right - text_width) / 2, (top + bottom - text_height) / 2),
        wrapped,
        font=text_font,
        fill=fill,
        spacing=spacing,
        align="center",
    )


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    color: str = BLUE,
    width: int = 7,
) -> None:
    draw.line((start, end), fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    length = 22
    spread = 0.55
    points = [
        end,
        (
            end[0] - length * math.cos(angle - spread),
            end[1] - length * math.sin(angle - spread),
        ),
        (
            end[0] - length * math.cos(angle + spread),
            end[1] - length * math.sin(angle + spread),
        ),
    ]
    draw.polygon(points, fill=color)


def title(draw: ImageDraw.ImageDraw, heading: str, subtitle: str | None = None) -> None:
    draw.text((80, 55), heading, font=font(48, bold=True), fill=INK)
    if subtitle:
        draw.text((82, 120), subtitle, font=font(24), fill=MUTED)


def save(image: Image.Image, name: str) -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    image.save(ASSET_DIR / name, quality=96)


def architecture_diagram() -> None:
    image = Image.new("RGB", (1800, 1020), CANVAS)
    draw = ImageDraw.Draw(image)
    title(draw, "Kiến trúc triển khai FaceTrust", "Tách rõ giao diện, API, suy luận và bằng chứng")

    boxes = [
        ((70, 265, 360, 520), "Trình duyệt", "Upload ảnh\nHiển thị kết luận", PALE_BLUE),
        ((430, 265, 735, 520), "FastAPI", "Kiểm tra tệp\n/api/detect", PALE_TEAL),
        ((810, 190, 1170, 595), "Pipeline suy luận", "Phát hiện khuôn mặt\nCrop + resize 224×224\nDetector chính + phụ", PAPER),
        ((1245, 190, 1725, 595), "Lớp trình bày", "Nhãn real/fake/uncertain\nChỉ số rủi ro\nBiên quyết định\nTín hiệu giải thích", PALE_GOLD),
    ]
    for box, heading, detail, fill in boxes:
        rounded_box(draw, box, fill=fill)
        center_text(draw, (box[0], box[1] + 25, box[2], box[1] + 105), heading, font(31, bold=True))
        center_text(draw, (box[0] + 12, box[1] + 115, box[2] - 12, box[3] - 22), detail, font(24), fill=MUTED)

    arrow(draw, (360, 392), (430, 392))
    arrow(draw, (735, 392), (810, 392))
    arrow(draw, (1170, 392), (1245, 392))

    rounded_box(draw, (170, 720, 715, 915), fill=PAPER)
    center_text(draw, (190, 735, 695, 790), "Checkpoint cục bộ", font(28, bold=True), fill=BLUE)
    center_text(
        draw,
        (195, 790, 690, 895),
        "MS-EffGCViT B0 - FaceForensics++\nEfficientNet-B0 phụ trợ khuôn mặt nhỏ",
        font(22),
        fill=MUTED,
    )
    rounded_box(draw, (920, 720, 1630, 915), fill=PAPER)
    center_text(draw, (940, 735, 1610, 790), "Dữ liệu và báo cáo kiểm chứng", font(28, bold=True), fill=GREEN)
    center_text(
        draw,
        (945, 790, 1605, 895),
        "data/benchmarks -> scripts/evaluate_cross_dataset.py\n-> reports/cross_dataset_results.json + .md",
        font(21),
        fill=MUTED,
    )
    arrow(draw, (990, 595), (990, 715), color=GREEN)
    arrow(draw, (570, 715), (910, 595), color=BLUE)
    save(image, "01_architecture.png")


def inference_pipeline() -> None:
    image = Image.new("RGB", (1800, 1060), PAPER)
    draw = ImageDraw.Draw(image)
    title(draw, "Full pipeline từ ảnh đầu vào đến kết luận", "Mỗi bước đều có điều kiện kiểm tra và đầu ra quan sát được")

    items = [
        ("01", "Nhận ảnh", "JPG/JFIF/PNG/WebP\nTối đa 16 MB", PALE_BLUE),
        ("02", "Xác thực", "Đọc ảnh thật\nChặn tệp lỗi", PALE_TEAL),
        ("03", "Định vị mặt", "Haar cascade\nChọn mặt chính", PALE_GOLD),
        ("04", "Chuẩn hóa", "Crop + margin\nResize 224×224", PALE_BLUE),
        ("05", "Suy luận", "p: detector chính\na: detector phụ", PALE_TEAL),
        ("06", "Quyết định", "Ngưỡng + điều kiện\nsmall-face", PALE_RED),
        ("07", "Trả kết quả", "Nhãn + điểm\nTín hiệu giải thích", PALE_GOLD),
    ]
    box_width = 210
    gap = 34
    start_x = 55
    top = 270
    for index, (number, heading, detail, fill) in enumerate(items):
        left = start_x + index * (box_width + gap)
        box = (left, top, left + box_width, top + 330)
        rounded_box(draw, box, fill=fill, radius=14)
        draw.text((left + 18, top + 18), number, font=font(22, bold=True), fill=BLUE)
        center_text(draw, (left + 10, top + 70, left + box_width - 10, top + 145), heading, font(27, bold=True))
        center_text(draw, (left + 12, top + 160, left + box_width - 12, top + 300), detail, font(20), fill=MUTED)
        if index < len(items) - 1:
            arrow(draw, (left + box_width + 4, top + 165), (left + box_width + gap - 4, top + 165), width=5)

    rounded_box(draw, (210, 750, 1590, 965), fill=CANVAS)
    center_text(draw, (235, 770, 1565, 825), "Điểm kiểm soát chất lượng", font(28, bold=True), fill=INK)
    notes = (
        "Không tìm thấy khuôn mặt -> UNCERTAIN  |  Demo được tách khỏi benchmark  |  "
        "Chỉ số hiển thị không được diễn giải như xác suất đúng  |  JSON lưu toàn bộ kết quả"
    )
    center_text(draw, (255, 825, 1545, 940), notes, font(22), fill=MUTED)
    save(image, "02_full_pipeline.png")


def score_mapping() -> None:
    image = Image.new("RGB", (1800, 1000), PAPER)
    draw = ImageDraw.Draw(image)
    title(draw, "Ánh xạ score nội bộ sang chỉ số hiển thị", "Ngưỡng ra quyết định được công khai; điểm không phải xác suất đúng")

    plot = (150, 250, 1650, 700)
    draw.line((plot[0], plot[3], plot[2], plot[3]), fill=INK, width=4)
    draw.line((plot[0], plot[1], plot[0], plot[3]), fill=INK, width=4)
    for tick in range(0, 11):
        x = plot[0] + (plot[2] - plot[0]) * tick / 10
        draw.line((x, plot[3], x, plot[3] + 12), fill=INK, width=2)
        draw.text((x - 18, plot[3] + 22), f"{tick / 10:.1f}", font=font(18), fill=MUTED)
    for tick in range(0, 9, 2):
        y = plot[3] - (plot[3] - plot[1]) * tick / 8
        draw.line((plot[0] - 12, y, plot[0], y), fill=INK, width=2)
        draw.text((plot[0] - 65, y - 12), f"{tick / 10:.1f}", font=font(18), fill=MUTED)

    points: list[tuple[float, float]] = []
    for step in range(101):
        p = step / 100
        risk = p if p < 0.5 else 0.5 + 0.3 * (p - 0.5) / 0.5
        x = plot[0] + (plot[2] - plot[0]) * p
        y = plot[3] - (plot[3] - plot[1]) * risk / 0.8
        points.append((x, y))
    draw.line(points, fill=RED, width=8, joint="curve")
    threshold_x = plot[0] + (plot[2] - plot[0]) * 0.5
    draw.line((threshold_x, plot[1], threshold_x, plot[3]), fill=GOLD, width=4)
    draw.text((threshold_x + 15, plot[1] + 10), "Ngưỡng p = 0,50", font=font(23, bold=True), fill=GOLD)
    draw.text((plot[2] - 180, plot[3] + 70), "Raw score p", font=font(23, bold=True), fill=INK)
    draw.text((40, plot[1] - 30), "Risk", font=font(23, bold=True), fill=INK)

    rounded_box(draw, (245, 810, 1555, 945), fill=PALE_GOLD, outline="#E7C986")
    center_text(
        draw,
        (275, 820, 1525, 935),
        "R(p) = p khi p < 0,50; R(p) = 0,50 + 0,30 × (p - 0,50) / 0,50 khi p ≥ 0,50. "
        "Giá trị tối đa của nhánh chính là 0,80.",
        font(22),
        fill=INK,
    )
    save(image, "03_score_mapping.png")


def ai_workflow() -> None:
    image = Image.new("RGB", (1800, 1040), CANVAS)
    draw = ImageDraw.Draw(image)
    title(draw, "Quy trình làm việc có AI hỗ trợ", "AI hỗ trợ phát triển; quyết định kỹ thuật được xác minh bằng mã và phép đo")
    items = [
        ("1", "Làm rõ bài toán", "Chuyển từ bảo vệ ảnh\nsang nhận diện deepfake"),
        ("2", "Khảo sát", "Dataset, checkpoint,\nkiến trúc và rủi ro"),
        ("3", "Lập kế hoạch", "Pipeline, UI, tiêu chí\nchấp nhận và benchmark"),
        ("4", "Triển khai", "FastAPI, detector,\nscore và giải thích"),
        ("5", "Đánh giá", "Cross-dataset, API,\nma trận nhầm lẫn"),
        ("6", "Lặp cải tiến", "Sửa lỗi, hiệu chỉnh,\nkiểm thử hồi quy"),
        ("7", "Tài liệu hóa", "README, đặc tả,\nbáo cáo và hướng dẫn"),
    ]
    center_y = 500
    box_width = 215
    gap = 27
    start_x = 40
    for index, (number, heading, detail) in enumerate(items):
        left = start_x + index * (box_width + gap)
        fill = PALE_BLUE if index % 2 == 0 else PALE_TEAL
        rounded_box(draw, (left, 320, left + box_width, 700), fill=fill, radius=16)
        draw.ellipse((left + 72, 345, left + 142, 415), fill=BLUE)
        center_text(draw, (left + 72, 345, left + 142, 415), number, font(28, bold=True), fill=PAPER)
        center_text(draw, (left + 12, 435, left + box_width - 12, 525), heading, font(25, bold=True))
        center_text(draw, (left + 12, 535, left + box_width - 12, 665), detail, font(19), fill=MUTED)
        if index < len(items) - 1:
            arrow(draw, (left + box_width + 2, center_y), (left + box_width + gap - 2, center_y), width=4)
    rounded_box(draw, (285, 820, 1515, 950), fill=PAPER)
    center_text(
        draw,
        (310, 835, 1490, 935),
        "Nguyên tắc kiểm chứng: mọi thay đổi phải qua ruff + pytest; mọi con số đánh giá phải sinh từ script; "
        "bộ demo không được dùng để công bố accuracy.",
        font(22),
        fill=INK,
    )
    save(image, "04_ai_workflow.png")


def demo_montage() -> None:
    files = [
        ("001_barack-obama.jpg", "Ảnh thật - 001"),
        ("002_portrait-01.jpg", "Ảnh thao túng - 002"),
        ("003_donald-trump.jpg", "Ảnh thật - 003"),
        ("004_portrait-02.jpg", "Ảnh thao túng - 004"),
    ]
    image = Image.new("RGB", (1800, 1050), CANVAS)
    draw = ImageDraw.Draw(image)
    title(draw, "Mẫu ảnh dùng cho trình diễn", "Số lẻ: ảnh thật; số chẵn: ảnh khuôn mặt đã bị thao túng")
    for index, (name, label) in enumerate(files):
        row, column = divmod(index, 2)
        left = 105 + column * 860
        top = 205 + row * 400
        box = (left, top, left + 730, top + 340)
        rounded_box(draw, box, fill=PAPER)
        source = Image.open(PROJECT_DIR / "data/demo-images" / name).convert("RGB")
        photo = ImageOps.fit(source, (300, 290), method=Image.Resampling.LANCZOS)
        image.paste(photo, (left + 25, top + 25))
        draw.text((left + 355, top + 85), label, font=font(28, bold=True), fill=RED if index % 2 else GREEN)
        draw.text((left + 355, top + 145), name, font=font(20), fill=MUTED)
        detail = "Nguồn ảnh thao túng có frame gốc trong SOURCES.md" if index % 2 else "Ảnh chân dung công khai từ Wikimedia Commons"
        wrapped = "\n".join(textwrap.wrap(detail, width=31))
        draw.multiline_text((left + 355, top + 195), wrapped, font=font(20), fill=INK, spacing=7)
    save(image, "05_demo_montage.png")


def ui_workflow() -> None:
    scan_path = Path(
        "C:/Users/quyng/AppData/Local/Temp/"
        "codex-clipboard-ffe26ca3-0ad2-4fb3-8d3c-930d41c7fc99.png"
    )
    image = Image.new("RGB", (1800, 1020), CANVAS)
    draw = ImageDraw.Draw(image)
    title(draw, "Giao diện kiểm định ảnh", "Trạng thái quét thực tế và cấu trúc kết quả trả về")
    rounded_box(draw, (80, 190, 860, 895), fill=PAPER)
    if scan_path.exists():
        source = Image.open(scan_path).convert("RGB")
        crop = source.crop((80, 90, min(source.width, 1280), min(source.height, 730)))
        fitted = ImageOps.fit(crop, (730, 610), method=Image.Resampling.LANCZOS)
        image.paste(fitted, (105, 215))
    draw.text((105, 845), "Trạng thái đang quét", font=font(25, bold=True), fill=INK)

    rounded_box(draw, (940, 190, 1720, 895), fill=PAPER)
    draw.text((990, 240), "KẾT QUẢ PHÂN TÍCH", font=font(20, bold=True), fill=RED)
    draw.text((990, 290), "Kết luận: nghi vấn giả mạo", font=font(34, bold=True), fill=INK)
    draw.text((990, 355), "Ví dụ face-swap do chủ dự án cung cấp", font=font(21), fill=MUTED)
    draw.line((990, 410, 1665, 410), fill=LINE, width=3)
    draw.text((990, 455), "CHỈ SỐ RỦI RO FAKE", font=font(18, bold=True), fill=MUTED)
    draw.text((990, 495), "58,8 / 100", font=font(38, bold=True), fill=RED)
    draw.text((1340, 455), "BIÊN QUYẾT ĐỊNH", font=font(18, bold=True), fill=MUTED)
    draw.text((1340, 495), "29,3%", font=font(38, bold=True), fill=TEAL)
    draw.line((990, 570, 1665, 570), fill=LINE, width=3)
    draw.text((990, 610), "TÍN HIỆU GIẢI THÍCH", font=font(19, bold=True), fill=INK)
    details = [
        "Detector chính: p = 0,6465 > ngưỡng 0,50",
        "Detector phụ: a = 0,4145; mặt chiếm 5,9% ảnh",
        "Kết luận theo nhánh chính; score chưa calibration",
    ]
    for index, detail in enumerate(details):
        y = 660 + index * 62
        draw.rectangle((995, y + 5, 1005, y + 38), fill=TEAL if index else RED)
        draw.text((1025, y), detail, font=font(20), fill=INK)
    save(image, "06_ui_workflow.png")


def dataset_chart(payload: dict[str, object]) -> None:
    datasets = payload["datasets"]
    assert isinstance(datasets, list)
    image = Image.new("RGB", (1800, 1000), PAPER)
    draw = ImageDraw.Draw(image)
    title(draw, "Quy mô tập đánh giá chéo", "Số frame thực tế được script sử dụng sau khi loại ảnh demo")

    chart_left, chart_top, chart_right, chart_bottom = 210, 260, 1600, 760
    draw.line((chart_left, chart_bottom, chart_right, chart_bottom), fill=INK, width=4)
    max_count = max(
        max(result["summary"]["expected_fake"], result["summary"]["expected_real"])
        for result in datasets
    )
    group_width = (chart_right - chart_left) / len(datasets)
    for index, result in enumerate(datasets):
        summary = result["summary"]
        center = chart_left + group_width * (index + 0.5)
        for offset, key, color, label in [
            (-100, "expected_fake", RED, "Fake"),
            (20, "expected_real", GREEN, "Real"),
        ]:
            count = summary[key]
            height = (chart_bottom - chart_top) * count / max_count
            box = (center + offset, chart_bottom - height, center + offset + 80, chart_bottom)
            draw.rounded_rectangle(box, radius=8, fill=color)
            draw.text((center + offset + 8, chart_bottom - height - 40), str(count), font=font(21, bold=True), fill=INK)
            draw.text((center + offset + 13, chart_bottom + 18), label, font=font(19), fill=MUTED)
        name = result["name"]
        bounds = draw.textbbox((0, 0), name, font=font(24, bold=True))
        draw.text((center - (bounds[2] - bounds[0]) / 2, 850), name, font=font(24, bold=True), fill=INK)
    draw.text((1180, 155), "Fake", font=font(22, bold=True), fill=RED)
    draw.text((1330, 155), "Real", font=font(22, bold=True), fill=GREEN)
    save(image, "07_dataset_size.png")


def benchmark_chart(payload: dict[str, object]) -> None:
    datasets = payload["datasets"]
    assert isinstance(datasets, list)
    rows = [*datasets, {"name": "Combined", "summary": payload["overall"]}]
    image = Image.new("RGB", (1800, 1080), CANVAS)
    draw = ImageDraw.Draw(image)
    title(draw, "Kết quả cross-dataset của pipeline hiện tại", "Đánh giá strict: uncertain được tính là sai")
    metrics = [
        ("strict_accuracy", "Accuracy", BLUE),
        ("fake_recall", "Fake recall", RED),
        ("real_recall", "Real recall", GREEN),
    ]
    left = 330
    top = 245
    bar_height = 42
    group_gap = 205
    width = 1250
    for group_index, row in enumerate(rows):
        y0 = top + group_index * group_gap
        draw.text((65, y0 + 42), row["name"], font=font(25, bold=True), fill=INK)
        for metric_index, (key, label, color) in enumerate(metrics):
            y = y0 + metric_index * 58
            value = float(row["summary"][key])
            draw.rounded_rectangle((left, y, left + width, y + bar_height), radius=9, fill="#E4EAF0")
            draw.rounded_rectangle((left, y, left + width * value, y + bar_height), radius=9, fill=color)
            draw.text((left + 12, y + 8), label, font=font(19, bold=True), fill=PAPER if value > 0.25 else INK)
            draw.text((left + width + 25, y + 6), f"{value * 100:.1f}%", font=font(22, bold=True), fill=INK)
    rounded_box(draw, (240, 895, 1560, 1015), fill=PALE_GOLD, outline="#E7C986")
    center_text(
        draw,
        (270, 905, 1530, 1005),
        "Kết quả phản ánh khả năng khái quát hóa ngoài miền huấn luyện. Chênh lệch fake recall và real recall "
        "cho thấy detector còn thiên lệch và chưa phù hợp để dùng như công cụ pháp chứng độc lập.",
        font(21),
        fill=INK,
    )
    save(image, "08_cross_dataset_metrics.png")


def confusion_matrix(payload: dict[str, object]) -> None:
    matrix = payload["overall"]["confusion_matrix"]
    values = [
        [matrix["true_fake_pred_fake"], matrix["true_fake_pred_real"], matrix["true_fake_pred_uncertain"]],
        [matrix["true_real_pred_fake"], matrix["true_real_pred_real"], matrix["true_real_pred_uncertain"]],
    ]
    image = Image.new("RGB", (1800, 1000), PAPER)
    draw = ImageDraw.Draw(image)
    title(draw, "Ma trận nhầm lẫn gộp", "Hàng là ground truth; cột là kết luận của hệ thống")
    x0, y0 = 510, 300
    cell_w, cell_h = 330, 220
    headers = ["Predicted fake", "Predicted real", "Uncertain"]
    row_names = ["True fake", "True real"]
    max_value = max(max(row) for row in values)
    for column, header in enumerate(headers):
        center_text(draw, (x0 + column * cell_w, 205, x0 + (column + 1) * cell_w, 285), header, font(24, bold=True))
    for row_index, row_name in enumerate(row_names):
        center_text(draw, (120, y0 + row_index * cell_h, 450, y0 + (row_index + 1) * cell_h), row_name, font(27, bold=True))
        for column, value in enumerate(values[row_index]):
            intensity = value / max(max_value, 1)
            if column == row_index:
                base = (21, 128, 93)
            elif column == 2:
                base = (181, 121, 24)
            else:
                base = (197, 58, 50)
            fill = tuple(int(248 - intensity * (248 - component)) for component in base)
            box = (
                x0 + column * cell_w + 8,
                y0 + row_index * cell_h + 8,
                x0 + (column + 1) * cell_w - 8,
                y0 + (row_index + 1) * cell_h - 8,
            )
            draw.rounded_rectangle(box, radius=16, fill=fill, outline=LINE, width=2)
            center_text(draw, box, str(value), font(49, bold=True), fill=INK)
    rounded_box(draw, (310, 820, 1490, 940), fill=CANVAS)
    center_text(
        draw,
        (335, 830, 1465, 930),
        "Đọc ma trận theo từng lớp giúp phát hiện thiên lệch mà một con số accuracy duy nhất có thể che khuất.",
        font(22),
        fill=MUTED,
    )
    save(image, "09_confusion_matrix.png")


def main() -> None:
    architecture_diagram()
    inference_pipeline()
    score_mapping()
    ai_workflow()
    demo_montage()
    ui_workflow()
    if REPORT_JSON.exists():
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        dataset_chart(payload)
        benchmark_chart(payload)
        confusion_matrix(payload)
    print(f"Generated report assets in {ASSET_DIR}")


if __name__ == "__main__":
    main()
