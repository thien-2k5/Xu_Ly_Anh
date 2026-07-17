# Đặc Tả Hệ Thống FaceTrust

Tài liệu này dùng làm nguồn chính để viết phần đặc tả trong báo cáo Word và phần giới thiệu kỹ thuật trong PowerPoint.

## 1. Thông Tin Chung

| Mục | Nội dung |
| --- | --- |
| Tên hệ thống | FaceTrust |
| Bài toán | Nhận diện ảnh khuôn mặt có khả năng là real hoặc fake |
| Loại ứng dụng | Web app local |
| Backend | FastAPI |
| Frontend | Vanilla HTML/CSS/JavaScript |
| Model chính | Face-crop deepfake detector |
| Model bổ trợ | Checkpoint crop cho khuôn mặt nhỏ |
| Input | Ảnh JPG, JPEG, JFIF, PNG, WebP |
| Output | Kết luận real/fake/uncertain, risk index, decision margin, tín hiệu giải thích |

## 2. Mục Tiêu Hệ Thống

FaceTrust được xây dựng nhằm hỗ trợ kiểm tra nhanh một ảnh khuôn mặt nghi ngờ bị tạo hoặc chỉnh sửa bằng AI/deepfake. Hệ thống không thay thế giám định pháp lý, nhưng cung cấp một pipeline thực nghiệm gồm upload ảnh, xử lý ảnh, chạy detector, hiển thị kết quả và ghi nhận các tín hiệu giải thích.

Mục tiêu cụ thể:

- Xây dựng web app có thể upload và kiểm tra ảnh.
- Tạo quy trình xử lý ảnh từ đầu vào đến kết luận.
- Tích hợp local detector để phân loại real/fake.
- Hiển thị kết quả theo cách dễ hiểu cho người dùng.
- Bổ sung benchmark/full pipeline evaluation để đánh giá hệ thống.
- Ghi nhận giới hạn hiện tại của model và hướng cải thiện.

## 3. Phạm Vi Và Giới Hạn

### 3.1. Phạm Vi

Hệ thống tập trung vào ảnh tĩnh có khuôn mặt. Người dùng chọn một ảnh từ máy tính, hệ thống phân tích và trả về kết luận.

Các chức năng nằm trong phạm vi:

- Upload ảnh.
- Validate định dạng và dung lượng.
- Phát hiện khuôn mặt.
- Chạy detector.
- Tạo risk index và decision margin.
- Hiển thị giải thích.
- Chạy benchmark trên bộ ảnh demo/evaluation.

### 3.2. Ngoài Phạm Vi

Các phần chưa nằm trong phạm vi bản hiện tại:

- Nhận diện video deepfake.
- Xác minh danh tính người trong ảnh.
- Kết luận pháp lý.
- Training lại model quy mô lớn trong giao diện web.
- Quản lý tài khoản người dùng.
- Lưu lịch sử scan lâu dài.

## 4. Yêu Cầu Chức Năng

| Mã | Yêu cầu | Mô tả | Trạng thái |
| --- | --- | --- | --- |
| FR-01 | Upload ảnh | Người dùng chọn ảnh từ máy tính | Đã có |
| FR-02 | Kiểm tra định dạng | Chỉ nhận JPG/JPEG/JFIF/PNG/WebP | Đã có |
| FR-03 | Giới hạn dung lượng | Từ chối ảnh vượt quá 16 MB | Đã có |
| FR-04 | Phân tích ảnh | Backend chạy detector và trả nhãn | Đã có |
| FR-05 | Hiển thị kết luận | UI hiển thị real/fake/uncertain | Đã có |
| FR-06 | Hiển thị risk score | UI hiển thị điểm rủi ro fake | Đã có |
| FR-07 | Hiển thị decision margin | UI hiển thị khoảng cách tới ngưỡng | Đã có |
| FR-08 | Giải thích kết quả | UI hiển thị các tín hiệu giải thích | Đã có |
| FR-09 | Scan animation | UI có trạng thái đang quét trước khi trả kết quả | Đã có |
| FR-10 | Phân tích đa nhánh | Đối chiếu detector chính và detector phụ | Đã có |
| FR-11 | Benchmark | Script đánh giá tự động qua API | Đã có |

## 5. Yêu Cầu Phi Chức Năng

| Mã | Yêu cầu | Mô tả |
| --- | --- | --- |
| NFR-01 | Dễ dùng | Người dùng chỉ cần chọn ảnh và bấm quét |
| NFR-02 | Minh bạch | Kết quả có tín hiệu giải thích, không chỉ có nhãn |
| NFR-03 | Bảo mật | Không cần gửi ảnh tới dịch vụ AI bên ngoài |
| NFR-04 | Không lưu upload lâu dài | Ảnh upload được xử lý trong thư mục tạm |
| NFR-05 | Có kiểm thử | Có unit test và script benchmark |
| NFR-06 | Giao diện gọn | Không hiển thị ảnh demo sẵn trên web |
| NFR-07 | Có tài liệu | Có README, evaluation, workflow và implementation notes |

## 6. Kiến Trúc Hệ Thống

```text
Người dùng
  -> Trình duyệt
  -> Frontend HTML/CSS/JS
  -> POST /api/detect
  -> FastAPI backend
  -> Validate ảnh
  -> Lưu tạm ảnh trong TemporaryDirectory
  -> Detector chính trên crop khuôn mặt
  -> Detector phụ cho trường hợp khuôn mặt nhỏ
  -> Response JSON
  -> UI hiển thị kết luận
```

Thành phần chính:

| Thành phần | File | Vai trò |
| --- | --- | --- |
| FastAPI app | `src/facetrust_benchmark/web.py` | Định nghĩa route và API |
| Upload pipeline | `src/facetrust_benchmark/detector_storage.py` | Xử lý upload, gọi detector, tạo response |
| Detector | `src/facetrust_benchmark/deepfake_detector.py` | Chạy model local và tạo evidence |
| Frontend | `src/facetrust_benchmark/static/` | Giao diện web |
| Benchmark | `scripts/evaluate_system.py` | Đánh giá full pipeline |

## 7. Đặc Tả API

### 7.1. `GET /api/health`

Mục đích: kiểm tra backend sẵn sàng.

Response chính:

```json
{
  "status": "ok",
  "service": "FaceTrust Deepfake Detector",
  "task": "image-deepfake-detection",
  "engine": "ai-vision-core"
}
```

### 7.2. `POST /api/detect`

Mục đích: nhận ảnh upload và trả kết quả phân tích.

Input:

| Field | Kiểu | Mô tả |
| --- | --- | --- |
| `image` | file | Ảnh cần kiểm tra |

Output chính:

| Field | Mô tả |
| --- | --- |
| `label` | Nhãn model: `real`, `fake` hoặc `uncertain` |
| `face_detected` | Có phát hiện khuôn mặt hay không |
| `scan_id` | Mã định danh ngắn của lượt quét |
| `presentation.verdict_label` | Nhãn hiển thị |
| `presentation.fake_risk_index` | Điểm rủi ro fake đã nén để trình bày |
| `presentation.decision_margin` | Khoảng cách chuẩn hóa tới ngưỡng quyết định |
| `presentation.signals` | Các tín hiệu giải thích |

## 8. Đặc Tả Giao Diện

Giao diện gồm hai vùng chính:

- Vùng chọn ảnh: upload file và bắt đầu kiểm định.
- Vùng kết quả: kết luận, risk index, decision margin, thông tin scan và tín hiệu giải thích.

Trạng thái giao diện:

| Trạng thái | Mô tả |
| --- | --- |
| Chờ quét | Chưa có ảnh hoặc chưa bấm quét |
| Đang quét | Hiển thị scan animation và progress |
| Real | Kết quả nghiêng về ảnh thật |
| Fake | Kết quả nghiêng về ảnh giả |
| Lỗi | Ảnh không hợp lệ hoặc backend lỗi |

## 9. Bộ Ảnh Demo/Evaluation

Thư mục:

```text
data/demo-images
```

Quy ước:

- Số lẻ: real.
- Số chẵn: fake / AI-generated / deepfake.

Tên file không ghi nhãn real/fake để khi demo nhìn tự nhiên hơn. Ví dụ:

```text
001_barack-obama.jpg
002_donald-trump.jpg
003_donald-trump.jpg
```

Nguồn ảnh:

```text
data/demo-images/SOURCES.md
```

## 10. Đặc Tả Đánh Giá

Script đánh giá:

```text
scripts/evaluate_system.py
```

Lệnh chạy:

```powershell
$env:PYTHONPATH='D:\Xampp\htdocs\anti-deepfake-face\src'
.\.venv\Scripts\python.exe scripts\evaluate_system.py
```

Report:

```text
reports/evaluation_results.md
reports/evaluation_results.json
```

Các metric:

- Accuracy
- Precision / Recall / F1 cho class fake
- Precision / Recall / F1 cho class real
- Confusion matrix
- Face detection rate
- API success rate
- Latency mean / median / p95 / max

Kết quả hiện tại được sinh tự động tại `reports/evaluation_results.*` và
`reports/cross_dataset_results.*`. Không chép số tĩnh vào đặc tả vì kết quả phải
được cập nhật cùng phiên bản checkpoint/ngưỡng.

## 11. Rủi Ro Và Hướng Cải Thiện

Rủi ro hiện tại:

- Model có thể bỏ sót ảnh fake ngoài domain train.
- Bộ ảnh evaluation còn nhỏ.
- Ảnh AI-generated không phải lúc nào cũng thuộc dạng face-swap nên detector khó nhận diện.
- Hai detector cục bộ có thể lệch nhau và còn hạn chế ngoài miền huấn luyện.

Hướng cải thiện:

- Thu thập thêm dataset đa nguồn.
- Fine-tune model trên ảnh AI-generated public-figure.
- Tách train/validation/test/cross-dataset rõ ràng.
- Hiệu chuẩn confidence bằng validation set.
- Báo cáo metric theo từng nhóm ảnh.
