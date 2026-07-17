# FaceTrust

FaceTrust là web app kiểm định ảnh khuôn mặt và đưa ra kết luận `real`, `fake`
hoặc `uncertain`, kèm chỉ số rủi ro, biên quyết định và tín hiệu giải thích.

Mục tiêu của bản hiện tại là xây dựng một pipeline nhận diện ảnh hoàn chỉnh để trình bày đồ án:

```text
chọn ảnh -> định vị mặt -> chạy hai detector -> kết luận -> giải thích
```

## Chức Năng Chính

- Upload ảnh JPG, JFIF, PNG hoặc WebP.
- Kiểm tra định dạng và dung lượng ảnh.
- Phát hiện vùng khuôn mặt.
- Chạy local detector để dự đoán `real` hoặc `fake`.
- Hiển thị `fake risk index` và biên so với ngưỡng quyết định.
- Hiển thị các tín hiệu giải thích kết quả.
- Có script benchmark/full pipeline evaluation sinh báo cáo tự động.

## Chạy Web

```powershell
cd D:\Xampp\htdocs\anti-deepfake-face
.\start-web.ps1
```

Mở:

[http://127.0.0.1:8000](http://127.0.0.1:8000)

## Bộ Ảnh Demo

Bộ ảnh demo nằm tại:

```text
data/demo-images
```

Quy ước ground truth:

- File bắt đầu bằng số lẻ là ảnh real.
- File bắt đầu bằng số chẵn là ảnh khuôn mặt đã bị thao túng/face-swap.

Ví dụ:

```text
001_barack-obama.jpg
002_portrait-01.jpg
003_donald-trump.jpg
```

Web không hiển thị sẵn các ảnh demo. Khi trình bày, bấm **Chọn ảnh** và chọn trực tiếp ảnh trong thư mục này.

Nguồn ảnh được ghi tại:

[data/demo-images/SOURCES.md](data/demo-images/SOURCES.md)

## Nguồn Gốc Model

- Model chính là checkpoint `MS-EffGCViT B0` công khai, đã được tác giả huấn luyện trên FaceForensics++. Nhóm không tuyên bố đã train model này từ random initialization.
- Model phụ là checkpoint `EfficientNet-B0` trong `models/deepfake_detector.pt`, chỉ hỗ trợ khi khuôn mặt chiếm dưới 12% diện tích ảnh.
- Đóng góp của dự án là lựa chọn checkpoint, tích hợp suy luận cục bộ, thiết kế ngưỡng/quy tắc quyết định, xây dựng web/API, kiểm thử và đánh giá chéo.

Trọng số được lưu trong:

```text
models/hf/koreapeter-ms-eff-gcvit-b0-ffpp/model.safetensors
models/deepfake_detector.pt
```

## Đánh Giá Và Benchmark

Chạy full-pipeline evaluation trên bộ demo:

```powershell
$env:PYTHONPATH='D:\Xampp\htdocs\anti-deepfake-face\src'
.\.venv\Scripts\python.exe scripts\evaluate_system.py
```

Chạy cross-dataset benchmark độc lập với bộ demo:

```powershell
$env:PYTHONPATH='D:\Xampp\htdocs\anti-deepfake-face\src'
.\.venv\Scripts\python.exe scripts\evaluate_cross_dataset.py --limit-per-class 100
```

Kết quả sinh ra:

- [reports/evaluation_results.md](reports/evaluation_results.md)
- [reports/evaluation_results.json](reports/evaluation_results.json)
- [reports/cross_dataset_results.md](reports/cross_dataset_results.md)
- [reports/cross_dataset_results.json](reports/cross_dataset_results.json)

Tài liệu phương pháp đánh giá:

- [docs/EVALUATION.md](docs/EVALUATION.md)

Không dùng bộ demo để công bố accuracy. Hãy đánh giá trên tập độc lập và báo cáo
riêng fake recall, real recall, false positive và số mẫu `uncertain`.

## Quy Trình Làm Việc Với AI

Tài liệu mô tả cách sử dụng AI trong quá trình phát triển:

- [docs/AI_WORKFLOW.md](docs/AI_WORKFLOW.md)

Nội dung gồm:

- Phân tích và điều chỉnh yêu cầu.
- Khảo sát dataset/model.
- Tái cấu trúc giao diện.
- Kiểm tra nhiều checkpoint và hiệu chỉnh pipeline.
- Viết script benchmark.
- Kiểm thử và viết tài liệu.

## Tài Liệu Cho Word Và PowerPoint

Các file này dùng trực tiếp để bạn làm báo cáo Word và slide:

- [docs/SYSTEM_SPECIFICATION.md](docs/SYSTEM_SPECIFICATION.md): đặc tả hệ thống.
- [docs/WORD_REPORT_OUTLINE.md](docs/WORD_REPORT_OUTLINE.md): dàn ý báo cáo Word.
- [docs/PPT_STORYBOARD.md](docs/PPT_STORYBOARD.md): storyboard từng slide PowerPoint.
- [docs/ASSET_CHECKLIST.md](docs/ASSET_CHECKLIST.md): checklist hình ảnh, bảng biểu và file cần mở.

## Ghi Chú Triển Khai

Xem:

- [docs/IMPLEMENTATION_NOTES.md](docs/IMPLEMENTATION_NOTES.md)

Tài liệu này mô tả kiến trúc, API, presentation score, demo images, cách chạy benchmark và lưu ý bảo mật.

## Cấu Trúc Dự Án

```text
src/facetrust_benchmark/
  web.py                 FastAPI app
  detector_storage.py    upload pipeline
  deepfake_detector.py   local detector
  static/                frontend HTML/CSS/JS

data/demo-images/        bộ ảnh trình diễn, không dùng để công bố accuracy tổng quát
data/benchmarks/         frame đánh giá cross-dataset
docs/                    tài liệu quy trình và đánh giá
reports/                 kết quả benchmark sinh tự động
scripts/                 script đánh giá hệ thống
tests/                   test backend
models/                  model local
```

## Kiểm Thử

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests scripts
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.\.venv\Scripts\python.exe -m pytest -q
```
