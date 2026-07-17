# Đánh Giá Model Và Full Pipeline

Tài liệu này mô tả cách đánh giá hệ thống FaceTrust ở hai cấp độ:

- Cấp độ model: model dự đoán ảnh `real` hay `fake` có đúng với ground truth không.
- Cấp độ full pipeline: toàn bộ luồng từ upload ảnh đến kết quả trên giao diện có hoạt động ổn định không.

## 1. Phạm Vi Đánh Giá

Hệ thống hiện tại là một web detector ảnh khuôn mặt. Người dùng chọn ảnh, backend kiểm tra định dạng, đọc ảnh, phát hiện khuôn mặt, chạy detector, tổng hợp các tín hiệu giải thích và trả kết quả cho UI.

Backend chính:

- API: `POST /api/detect`
- Local detector: `src/facetrust_benchmark/deepfake_detector.py`
- Upload pipeline: `src/facetrust_benchmark/detector_storage.py`
- UI: `src/facetrust_benchmark/static/`
- Bộ ảnh demo/evaluation: `data/demo-images`

## 2. Bộ Ảnh Đánh Giá

Bộ ảnh hiện tại nằm tại `data/demo-images`.

Quy ước ground truth:

- File bắt đầu bằng số lẻ là ảnh real.
- File bắt đầu bằng số chẵn là ảnh fake / AI-generated / deepfake.

Bộ ảnh được dùng như một public-figure stress set: có ảnh thật của người nổi tiếng và ảnh AI-generated/public-figure từ nguồn công khai. Mục tiêu của bộ này không phải làm số liệu đẹp, mà để kiểm tra xem detector có chịu được ảnh ngoài domain train hay không.

Nguồn ảnh được ghi trong `data/demo-images/SOURCES.md`.

## 3. Cách Chạy Benchmark

Chạy lệnh:

```powershell
$env:PYTHONPATH='D:\Xampp\htdocs\anti-deepfake-face\src'
.\.venv\Scripts\python.exe scripts\evaluate_system.py
```

Kết quả sinh ra:

- `reports/evaluation_results.json`
- `reports/evaluation_results.md`

Script này post từng ảnh qua chính API `/api/detect`, vì vậy nó đo pipeline thật thay vì gọi model riêng lẻ.

## 4. Metric Được Tính

Model-level metrics:

- Accuracy
- Precision cho class fake
- Recall cho class fake
- F1-score cho class fake
- Precision/Recall/F1 cho class real
- Confusion matrix

Pipeline-level metrics:

- API success rate
- Face detection rate
- Latency mean / median / p95 / max
- Kết quả từng ảnh

## 5. Kết Quả Hiện Tại

Kết quả benchmark mới nhất được lưu tại `reports/evaluation_results.md`.

Tóm tắt lần chạy hiện tại:

- Tổng số ảnh: 24
- API success rate: 100.0%
- Face detection rate: 91.7%
- Accuracy trên public-figure stress set: 50.0%
- Fake recall: 0.0%
- Real recall: 100.0%

Diễn giải:

Hệ thống upload, xử lý ảnh và trả kết quả ổn định ở cấp pipeline. Tuy nhiên, model local hiện tại đang rất bảo thủ với nhóm ảnh AI-generated/public-figure: nhiều ảnh fake ngoài domain train bị dự đoán là real. Đây là kết quả quan trọng vì nó chỉ ra giới hạn thật của model hiện tại.

Nói cách khác, pipeline đã chạy được end-to-end, nhưng model chưa đủ mạnh để khẳng định nhận diện tốt mọi loại ảnh giả trên Internet.

## 6. Full Pipeline Evaluation

Pipeline được đánh giá theo các bước:

1. Health check: gọi `/api/health` để xác nhận backend sẵn sàng.
2. Input validation: ảnh phải đúng định dạng JPG/PNG/WebP/JFIF và không quá giới hạn dung lượng.
3. Upload: gửi ảnh qua endpoint `/api/detect`.
4. Image loading: backend mở ảnh và chuẩn hóa dữ liệu ảnh.
5. Face detection: hệ thống kiểm tra có vùng khuôn mặt hay không.
6. Model inference: detector trả nhãn `real`, `fake` hoặc `uncertain`.
7. Presentation scoring: backend tạo `fake_risk_index` và `decision_margin`;
   margin là khoảng cách tới ngưỡng, không phải xác suất đúng.
8. Evidence generation: backend tạo các tín hiệu giải thích như vùng mặt hợp lệ, đối chiếu đa nhánh, điểm rủi ro.
9. UI rendering: frontend hiển thị kết luận, risk index, decision margin và lý do.

## 7. Nhận Xét Kỹ Thuật

Điểm mạnh hiện tại:

- Web app đã có luồng sử dụng rõ: chọn ảnh, quét, kết luận.
- API hoạt động ổn định trên toàn bộ bộ ảnh demo.
- Có benchmark tự động, có báo cáo Markdown/JSON.
- UI không định sẵn nhãn trả về và không hiển thị ảnh mẫu sẵn trên web.
- Có `decision_margin` thận trọng, không trình bày như xác suất chắc chắn đúng.

Giới hạn hiện tại:

- Detector hiện tại chưa ổn với ảnh AI-generated tổng quát.
- Bộ ảnh demo còn nhỏ, chưa đủ để kết luận độ chính xác thực tế.
- Một số ảnh fake không có mặt rõ hoặc không thuộc dạng face-swap, khiến detector khó nhận diện.
- Không dùng dịch vụ AI bên ngoài trong kết luận; hai detector đều chạy cục bộ.

## 8. Hướng Cải Thiện

Để nâng cấp lên mức tốt hơn, cần:

- Bổ sung dataset đa nguồn gồm FaceForensics++, DFDC, Celeb-DF, ảnh AI-generated, ảnh nén từ mạng xã hội và ảnh thật cùng domain.
- Tách rõ train / validation / test / cross-dataset test.
- Fine-tune model trên dữ liệu ngoài face-swap, nhất là diffusion-generated portraits.
- Hiệu chuẩn xác suất bằng validation set để confidence có ý nghĩa hơn.
- Thêm threshold tuning cho từng domain ảnh.
- Báo cáo confusion matrix và F1-score theo từng nhóm: real, face-swap, reenactment, diffusion-generated, compressed image.
