# Dàn Ý Báo Cáo Word

Tài liệu này giúp viết báo cáo Word nhanh hơn. Có thể copy từng mục sang Word rồi chỉnh câu chữ theo yêu cầu của trường.

## Trang Bìa

Thông tin cần có:

- Tên trường/khoa.
- Tên môn học/đồ án.
- Tên đề tài: **FaceTrust - Hệ thống kiểm định ảnh real/fake bằng AI**.
- Thành viên nhóm.
- Giảng viên hướng dẫn.
- Thời gian thực hiện.

## Tóm Tắt Đề Tài

Nội dung gợi ý:

> Đề tài xây dựng hệ thống FaceTrust nhằm hỗ trợ kiểm định ảnh khuôn mặt có khả năng là real, fake hoặc chưa đủ bằng chứng. Hệ thống cho phép người dùng upload ảnh, định vị và crop khuôn mặt, chạy hai detector, rồi hiển thị chỉ số rủi ro, biên quyết định và các tín hiệu giải thích. Đề tài cũng xây dựng script benchmark để đánh giá cả cấp độ model và full pipeline.

## Chương 1. Giới Thiệu

### 1.1. Lý Do Chọn Đề Tài

Ý chính:

- Deepfake và ảnh AI-generated ngày càng phổ biến.
- Ảnh giả có thể gây hiểu nhầm, lừa đảo, ảnh hưởng truyền thông và uy tín cá nhân.
- Cần một công cụ kiểm tra nhanh để hỗ trợ người dùng đánh giá ảnh nghi ngờ.
- Đề tài phù hợp với hướng ứng dụng AI trong an toàn thông tin và xử lý ảnh.

### 1.2. Mục Tiêu Đề Tài

Mục tiêu:

- Xây dựng web app kiểm tra ảnh real/fake.
- Tạo pipeline xử lý ảnh end-to-end.
- Tích hợp model nhận diện ảnh deepfake.
- Hiển thị kết quả dễ hiểu.
- Có benchmark đánh giá model và pipeline.
- Ghi nhận giới hạn kỹ thuật và hướng phát triển.

### 1.3. Phạm Vi Đề Tài

Nằm trong phạm vi:

- Ảnh tĩnh.
- Ảnh khuôn mặt.
- Upload từng ảnh.
- Phân loại real/fake.
- Evaluation trên bộ ảnh demo/evaluation.

Ngoài phạm vi:

- Video deepfake.
- Xác minh danh tính.
- Kết luận pháp lý.
- Triển khai cloud production.
- Training model quy mô lớn trong giao diện.

## Chương 2. Cơ Sở Lý Thuyết

### 2.1. Deepfake Và Ảnh AI-Generated

Nội dung cần viết:

- Deepfake là kỹ thuật dùng AI để thay đổi hoặc tạo nội dung khuôn mặt.
- Ảnh AI-generated có thể tạo người thật/nhân vật công chúng trong bối cảnh không có thật.
- Deepfake detector thường học các dấu hiệu bất thường về texture, vùng mặt, ánh sáng, nén ảnh hoặc đặc trưng model.

### 2.2. Bài Toán Phân Loại Real/Fake

Mô tả:

- Input: một ảnh khuôn mặt.
- Output: nhãn `real` hoặc `fake`.
- Đây là bài toán binary classification.
- Metric cần dùng: accuracy, precision, recall, F1-score, confusion matrix.

### 2.3. Full Pipeline Evaluation

Ý chính:

- Không chỉ đánh giá model riêng lẻ.
- Cần đánh giá toàn bộ pipeline: upload, validate, detect face, inference, response, UI.
- Pipeline tốt phải chạy ổn định, có tỉ lệ API success cao và latency hợp lý.

## Chương 3. Phân Tích Và Thiết Kế Hệ Thống

### 3.1. Yêu Cầu Chức Năng

Đưa bảng từ [SYSTEM_SPECIFICATION.md](SYSTEM_SPECIFICATION.md), mục 4.

### 3.2. Yêu Cầu Phi Chức Năng

Đưa bảng từ [SYSTEM_SPECIFICATION.md](SYSTEM_SPECIFICATION.md), mục 5.

### 3.3. Kiến Trúc Tổng Quan

Sơ đồ gợi ý:

```text
User -> Browser -> FastAPI backend -> Detector -> Response -> UI
```

Nên chụp hoặc vẽ lại thành sơ đồ trong Word/PPT.

### 3.4. Luồng Xử Lý Ảnh

Các bước:

1. Người dùng chọn ảnh.
2. Frontend gửi ảnh lên `/api/detect`.
3. Backend kiểm tra định dạng/dung lượng.
4. Ảnh được xử lý trong thư mục tạm.
5. Detector chạy inference.
6. Backend tạo risk score, confidence và signals.
7. Frontend hiển thị kết quả.

### 3.5. Thiết Kế Giao Diện

Ý chính:

- Giao diện được tối giản thành verification console.
- Không hiển thị sẵn ảnh demo để tránh cảm giác chỉ chạy case mẫu.
- Có scan animation để thể hiện quá trình xử lý.
- Kết quả gồm kết luận, điểm rủi ro, confidence và tín hiệu giải thích.

Hình cần chèn:

- Screenshot màn hình ban đầu.
- Screenshot đang quét.
- Screenshot kết quả real/fake.

## Chương 4. Triển Khai Hệ Thống

### 4.1. Công Nghệ Sử Dụng

| Thành phần | Công nghệ |
| --- | --- |
| Backend | FastAPI |
| Frontend | HTML/CSS/JavaScript |
| Xử lý ảnh | OpenCV, Pillow |
| Model | PyTorch/Transformers |
| Phân tích đa nhánh | Detector chính + detector phụ |
| Test | Pytest, Ruff |

### 4.2. Cấu Trúc Thư Mục

Đưa bảng:

| Thư mục/file | Vai trò |
| --- | --- |
| `src/facetrust_benchmark/web.py` | API backend |
| `src/facetrust_benchmark/detector_storage.py` | Upload pipeline |
| `src/facetrust_benchmark/deepfake_detector.py` | Detector |
| `src/facetrust_benchmark/static/` | Frontend |
| `data/demo-images/` | Bộ ảnh demo/evaluation |
| `scripts/evaluate_system.py` | Benchmark |
| `reports/` | Kết quả đánh giá |
| `docs/` | Tài liệu kỹ thuật |

### 4.3. API Chính

Mô tả:

- `GET /api/health`: kiểm tra hệ thống.
- `POST /api/detect`: gửi ảnh và nhận kết quả.

### 4.4. Detector phụ trợ

Viết ngắn:

Checkpoint EfficientNet-B0 được dùng có điều kiện khi khuôn mặt chiếm dưới 12%
khung hình. Detector phụ không tự quyết định trên ảnh có khuôn mặt đủ lớn.

## Chương 5. Đánh Giá Thực Nghiệm

### 5.1. Bộ Dữ Liệu Đánh Giá

Nội dung:

- 18 ảnh trong `data/demo-images` chỉ dùng để trình diễn.
- Số lẻ là real, số chẵn là fake/AI-generated.
- Nguồn ảnh công khai, ghi trong `SOURCES.md`.
- Bộ này dùng như public-figure stress set.

### 5.2. Phương Pháp Đánh Giá

Script:

```powershell
$env:PYTHONPATH='D:\Xampp\htdocs\anti-deepfake-face\src'
.\.venv\Scripts\python.exe scripts\evaluate_system.py
```

Metric:

- Accuracy.
- Precision/Recall/F1.
- Confusion matrix.
- API success rate.
- Face detection rate.
- Latency.

### 5.3. Kết Quả

Lấy số liệu mới nhất từ `reports/evaluation_results.md` và
`reports/cross_dataset_results.md`; chèn confusion matrix từ report cross-dataset.

### 5.4. Nhận Xét

Viết theo hướng:

- Pipeline chạy ổn định vì API success rate đạt 100%.
- Face detection rate đạt 91.7%, chứng tỏ phần xử lý ảnh hoạt động trên đa số ảnh.
- Model hiện tại còn yếu với ảnh AI-generated/public-figure ngoài domain train.
- Đây là cơ sở để đề xuất cải thiện bằng dataset đa nguồn và fine-tuning.

## Chương 6. Quy Trình Làm Việc Với AI

Dựa vào [AI_WORKFLOW.md](AI_WORKFLOW.md).

Các ý chính:

- AI hỗ trợ phân tích yêu cầu.
- AI hỗ trợ tái cấu trúc hệ thống.
- AI hỗ trợ viết code, UI, benchmark script.
- AI hỗ trợ kiểm thử và viết tài liệu.
- Nhóm vẫn kiểm tra và quyết định hướng cuối cùng.

Đoạn có thể copy:

> Nhóm sử dụng AI như trợ lý kỹ thuật trong quá trình phát triển. AI hỗ trợ phân tích yêu cầu, đề xuất kiến trúc, viết script benchmark, tái cấu trúc giao diện và tạo tài liệu. Tuy nhiên, các quyết định chính như điều chỉnh bài toán, chọn pipeline, đánh giá kết quả và trình bày giới hạn hệ thống đều do nhóm kiểm tra và xác nhận.

## Chương 7. Kết Luận Và Hướng Phát Triển

### 7.1. Kết Luận

Ý chính:

- Đã xây dựng được web app kiểm định ảnh real/fake.
- Hệ thống có pipeline upload -> detect -> result.
- Có giao diện trực quan.
- Có benchmark tự động.
- Có tài liệu quy trình làm việc với AI.

### 7.2. Hạn Chế

- Model chưa tốt với ảnh AI-generated ngoài domain.
- Bộ ảnh evaluation còn nhỏ.
- Chưa xử lý video.
- Chưa có calibration xác suất chuẩn.

### 7.3. Hướng Phát Triển

- Mở rộng dataset.
- Fine-tune model.
- Thêm cross-dataset benchmark.
- Thêm dashboard lịch sử scan.
- Triển khai cloud hoặc Docker.
- Nâng cấp sang ensemble checkpoint đã được đánh giá trên calibration set giữ riêng.

## Phụ Lục

Nên đưa:

- Danh sách ảnh demo.
- Nguồn ảnh.
- Kết quả benchmark chi tiết.
- Một vài ảnh chụp giao diện.
- Lệnh chạy web/test/benchmark.
