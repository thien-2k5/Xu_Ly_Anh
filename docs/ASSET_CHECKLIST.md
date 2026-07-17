# Checklist Hình Ảnh Và Bảng Biểu Cho Word/PPT

Tài liệu này liệt kê các ảnh chụp, bảng biểu và đoạn nội dung nên đưa vào báo cáo hoặc slide.

## 1. Ảnh Chụp Giao Diện Cần Có

| Mã | Nội dung cần chụp | Dùng trong |
| --- | --- | --- |
| IMG-01 | Trang chủ FaceTrust khi chưa chọn ảnh | Word chương giao diện, PPT slide 6 |
| IMG-02 | File picker mở thư mục `data/demo-images` | PPT slide 8 |
| IMG-03 | Ảnh đã được chọn và preview trên web | Word chương triển khai |
| IMG-04 | Trạng thái đang quét / scan animation | PPT slide 6 |
| IMG-05 | Kết quả một ảnh real | Word/PPT demo |
| IMG-06 | Kết quả một ảnh fake hoặc AI-generated | Word/PPT demo |
| IMG-07 | File `reports/evaluation_results.md` | PPT slide 9/10 |
| IMG-08 | Terminal chạy `pytest` pass | Phụ lục Word |
| IMG-09 | Terminal chạy `scripts/evaluate_system.py` | Word chương đánh giá |

## 2. Bảng Nên Đưa Vào Word

### Bảng công nghệ sử dụng

| Thành phần | Công nghệ |
| --- | --- |
| Backend | FastAPI |
| Frontend | HTML/CSS/JavaScript |
| Model | PyTorch/Transformers |
| Xử lý ảnh | OpenCV, Pillow |
| Nhánh phân tích | Detector chính + detector phụ |
| Test | Pytest, Ruff |

### Bảng yêu cầu chức năng

Lấy từ:

```text
docs/SYSTEM_SPECIFICATION.md
```

Mục:

```text
4. Yêu Cầu Chức Năng
```

### Bảng kết quả benchmark

Lấy từ:

```text
reports/evaluation_results.md
```

Mục:

```text
Summary Metrics
Confusion Matrix
Pipeline Timing
```

## 3. Sơ Đồ Nên Vẽ Lại

### Sơ đồ kiến trúc

```text
User
  -> Browser UI
  -> FastAPI Backend
  -> Local Detector
  -> Response JSON
  -> Result UI
```

Detector chính và detector phụ đều được nạp từ checkpoint cục bộ trong `models/`.

### Sơ đồ pipeline

```text
Select image
  -> Validate
  -> Load image
  -> Face detection
  -> Model inference
  -> Risk/decision-margin scoring
  -> Evidence signals
  -> UI result
```

### Sơ đồ quy trình làm việc với AI

```text
Requirement analysis
  -> Architecture planning
  -> Code implementation
  -> UI restructuring
  -> Benchmark scripting
  -> Testing
  -> Documentation
```

## 4. Nội Dung Có Thể Copy Vào Slide

### One-line project description

```text
FaceTrust là web app hỗ trợ kiểm định ảnh khuôn mặt real/fake bằng local detector, risk score và các tín hiệu giải thích.
```

### One-line evaluation statement

```text
Benchmark được chạy qua chính API /api/detect, vì vậy kết quả phản ánh full pipeline thay vì chỉ đo model riêng lẻ.
```

### One-line limitation statement

```text
Pipeline hiện hoạt động ổn định, nhưng model local cần được fine-tune thêm để nhận diện tốt hơn ảnh AI-generated ngoài domain train.
```

## 5. Ảnh Demo Nên Chọn Khi Trình Bày

Ảnh real dễ hiểu:

- `001_barack-obama.jpg`
- `003_donald-trump.jpg`
- `009_cristiano-ronaldo.jpg`
- `011_lionel-messi.jpg`

Ảnh fake/AI-generated dễ hiểu:

- `002_donald-trump.jpg`
- `004_donald-trump.jpg`
- `010_abraham-lincoln.jpg`
- `022_george-washington.jpg`

Lưu ý: ground truth dựa trên số thứ tự. Số lẻ là real, số chẵn là fake/AI-generated.

## 6. File Nên Mở Khi Giảng Viên Hỏi

| Câu hỏi | File nên mở |
| --- | --- |
| Hệ thống làm gì? | `README.md` |
| Đặc tả hệ thống đâu? | `docs/SYSTEM_SPECIFICATION.md` |
| Benchmark thế nào? | `docs/EVALUATION.md` và `reports/evaluation_results.md` |
| Quy trình làm việc với AI đâu? | `docs/AI_WORKFLOW.md` |
| Dùng ảnh nào demo? | `data/demo-images` |
| Nguồn ảnh đâu? | `data/demo-images/SOURCES.md` |
| Code API ở đâu? | `src/facetrust_benchmark/web.py` |
| Script đánh giá đâu? | `scripts/evaluate_system.py` |
